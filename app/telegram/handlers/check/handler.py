import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, Document
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.models.request_dto import XtreamRequestDTO
from app.utils.m3u_parser import M3UParser
from app.services.xtream import XtreamService
from app.services.batch_checker import BatchChecker

from app.utils.validators import (
    detect_input_type,
    parse_xtream_input,
    validate_xtream_input,
    is_batch_input,
    parse_batch_input,
)

from app.utils.formatter import (
    format_xtream_response,
    format_batch_progress,
    format_batch_report,
    format_date,
)

from app.core.exceptions import (
    XtreamError,
    InvalidCredentialsError,
    ServerNotRespondingError,
)

from config.settings import settings

logger = logging.getLogger(__name__)

router = Router(name="check-router")

xtream_service = XtreamService()
m3u_parser = M3UParser()
batch_checker = BatchChecker()

class BatchCheckState(StatesGroup):
    processing = State()


@router.message(CommandStart())
async def start_handler(message: Message):

    text = (
        "🔥 <b>Xtream Checker Bot</b>\n"
        "\n"
        "<b>Comandos disponibles:</b>\n"
        "\n"
        "🔍 <b>Cuenta individual:</b>\n"
        "Envia un link M3U o formato Xtream:\n"
        "<code>http://server:port username password</code>\n"
        "<code>http://server/get.php?username=xxx&password=xxx</code>\n"
        "\n"
        "📋 <b>Lista masiva:</b>\n"
        "Envia un archivo .txt con una cuenta por linea\n"
        "o pega las cuentas directamente (una por linea)\n"
        "\n"
        "❓ <b>/help</b> - Mas informacion"
    )

    await message.answer(text)


@router.message(Command("help"))
async def help_handler(message: Message):

    text = (
        "📚 <b>AYUDA</b>\n"
        "\n"
        "<b>Formatos aceptados:</b>\n"
        "\n"
        "<b>1. Xtream (3 partes):</b>\n"
        "<code>http://example.com:8080 user123 pass123</code>\n"
        "\n"
        "<b>2. Link M3U:</b>\n"
        "<code>http://example.com/get.php?username=xxx&password=xxx&type=m3u</code>\n"
        "\n"
        "<b>3. Lista masiva (.txt):</b>\n"
        "Un archivo con una cuenta por linea en cualquier formato\n"
        "\n"
        "<b>LIMITES:</b>\n"
        f"Maximo {settings.MAX_BATCH_SIZE} cuentas por lista\n"
        f"Delay entre checks: {settings.BATCH_DELAY}s\n"
        "\n"
        "<b>El bot detecta automaticamente:</b>\n"
        "✅ Cuentas validas (activas)\n"
        "❌ Credenciales invalidas\n"
        "⚠️ Servidores que no responden\n"
        "🌎 Contenido en espanol/latino"
    )

    await message.answer(text)


@router.message(Command("batch"))
async def batch_help(message: Message):
    text = (
        "📋 <b>CHECK MASIVO</b>\n"
        "\n"
        "Para verificar una lista de cuentas:\n"
        "\n"
        "1. Envia un archivo <b>.txt</b> con las cuentas\n"
        "2. O pega las cuentas directamente (una por linea)\n"
        "\n"
        "<b>Formatos en la lista:</b>\n"
        "• Xtream: <code>http://server:port user pass</code>\n"
        "• M3U: <code>http://server/get.php?username=x&password=y</code>\n"
        "• Puedes mezclar ambos formatos\n"
        "\n"
        f"<b>Limite:</b> {settings.MAX_BATCH_SIZE} cuentas"
    )
    await message.answer(text)


@router.message(F.document)
async def handle_file_upload(message: Message, state: FSMContext = None):
    if message.document.file_size > 500_000:
        await message.answer("❌ El archivo es demasiado grande (max 500KB)")
        return

    if message.document.file_name and not message.document.file_name.endswith(".txt"):
        await message.answer("❌ Solo se aceptan archivos .txt")
        return

    file_info = await message.bot.get_file(message.document.file_id)
    content_bytes = await message.bot.download_file(file_info.file_path)
    content = content_bytes.decode("utf-8", errors="ignore")
    await _process_batch(message, content, state)


@router.message(Command("cancel"), BatchCheckState.processing)
async def cancel_batch(message: Message, state: FSMContext):
    await message.answer("❌ Proceso cancelado")
    await state.clear()


@router.message()
async def check_handler(message: Message, state: FSMContext = None):

    text = message.text

    if not text:
        return

    logger.info(f"[MESSAGE] {message.from_user.id}: {text[:50]}...")

    if is_batch_input(text):
        await _process_batch(message, text, state)
        return

    await _check_single(message, text)


async def _check_single(message: Message, text: str):

    try:
        input_type = detect_input_type(text)

        if input_type == "m3u":
            logger.info(f"[M3U] Parsing URL")
            parsed = m3u_parser.parse(text)
            server = parsed["server"]
            username = parsed["username"]
            password = parsed["password"]

        elif input_type == "xtream":
            server, username, password = parse_xtream_input(text)

            if not server or not username or not password:
                await message.answer(
                    "❌ Formato invalido.\n\n"
                    "Envia:\n"
                    "<code>http://server:port username password</code>"
                )
                return

        else:
            await message.answer(
                "❌ Formato invalido.\n\n"
                "Envia:\n"
                "<code>http://server:port username password</code>\n\n"
                "o un link M3U."
            )
            return

        is_valid, error = validate_xtream_input(server, username, password)

        if not is_valid:
            await message.answer(f"❌ {error}")
            return

        dto = XtreamRequestDTO(
            server=server,
            username=username,
            password=password
        )

        loading = await message.answer("🔍 Verificando cuenta...\n⏳ Escaneando contenido...")

        result = await xtream_service.check_account(dto)
        summary = xtream_service.extract_summary(result)

        try:
            spanish = await xtream_service.check_spanish_content(dto)
            summary["spanish_content"] = spanish
        except Exception as e:
            logger.warning(f"[LANG] No se pudo detectar contenido: {e}")

        response = format_xtream_response(summary)

        await loading.edit_text(response)

    except InvalidCredentialsError:
        await message.answer("❌ <b>Credenciales invalidas</b>\n\nLa cuenta no existe o la contrasena es incorrecta.")

    except ServerNotRespondingError:
        await message.answer("❌ <b>El servidor no responde</b>\n\nEl servidor puede estar caido o bloqueando la conexion.")

    except XtreamError as e:
        await message.answer(f"❌ {str(e)}")

    except Exception as e:
        logger.exception(f"[UNHANDLED ERROR] {str(e)}")
        await message.answer("❌ Error interno del sistema")


async def _process_batch(message: Message, content: str, state: FSMContext = None):

    entries = parse_batch_input(content)

    if not entries:
        await message.answer(
            "❌ No se encontraron cuentas validas.\n\n"
            "Formatos aceptados:\n"
            "<code>http://server:port username password</code>\n"
            "<code>http://server/get.php?username=x&password=y</code>"
        )
        return

    if len(entries) > settings.MAX_BATCH_SIZE:
        await message.answer(
            f"❌ Demasiadas cuentas ({len(entries)}).\n"
            f"Maximo: {settings.MAX_BATCH_SIZE}"
        )
        return

    await message.answer(
        f"📋 <b>Iniciando check masivo...</b>\n"
        f"\n"
        f"Cuentas a verificar: <b>{len(entries)}</b>"
    )

    if state:
        await state.set_state(BatchCheckState.processing)

    progress_msg = await message.answer("⏳ Preparando...")

    async def on_progress(current, total, report):
        text = format_batch_progress(current, total, report)
        try:
            await progress_msg.edit_text(text)
        except:
            pass

    report = await batch_checker.check_list(entries, on_progress)

    final_text = format_batch_report(report)

    if len(final_text) > 4000:
        valid_only = [r for r in report.results if r.status == "valid"]
        lines = ["<b>CUENTAS VALIDAS:</b>", ""]
        for r in valid_only:
            exp = format_date(r.expiration) if r.expiration else "N/A"
            lines.append(f"  ✅ <code>{r.username}</code> | {r.server} | Exp: {exp}")
        final_text = "\n".join(lines) if lines else "<b>No se encontraron cuentas validas</b>"

    await progress_msg.edit_text(final_text)

    if state:
        await state.clear()
