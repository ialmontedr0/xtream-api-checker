from datetime import datetime

def format_date(timestamp):
    if not timestamp:
        return "N/A"
    
    try:
        return datetime.fromtimestamp(
            int(timestamp)
        ).strftime("%Y-%m-%d %H:%M:%S")
        
    except:
        return "N/A"

def format_spanish_content(content: dict) -> str:
    parts = ["", "<b>🌎 CONTENIDO LATINO:</b>"]

    ch = content.get("channels", {})
    mv = content.get("movies", {})
    sr = content.get("series", {})

    def line(emoji, label, info):
        if info.get("has"):
            return f"{emoji} <b>{label}:</b> {info['count']}/{info['total']} en espanol/latino"
        else:
            return f"{emoji} <b>{label}:</b> No detectado"

    parts.append(line("📺", "Canales", ch))
    parts.append(line("🎬", "Peliculas", mv))
    parts.append(line("📺", "Series", sr))

    return "\n".join(parts)

def format_xtream_response(data: dict) -> str:
    main = (
        "<b>CUENTA VALIDA</b>\n"
        "\n"
        f"<b>Usuario:</b> {data.get('username', 'N/A')}\n"
        f"<b>Contrasena:</b> {data.get('password', 'N/A')}\n"
        f"<b>Estado:</b> {data.get('status', 'N/A')}\n"
        f"<b>Expira:</b> {format_date(data.get('expiration'))}\n"
        f"<b>Creada:</b> {format_date(data.get('created_at'))}\n"
        f"<b>Conexiones:</b> {data.get('active_connections', '?')} / {data.get('max_connections', '?')}\n"
        f"<b>Zona horaria:</b> {data.get('timezone', 'N/A')}\n"
        f"<b>Servidor:</b> {data.get('server_url', 'N/A')}"
    )

    spanish = data.get("spanish_content")
    if spanish:
        main += format_spanish_content(spanish)

    return main

def format_batch_progress(current: int, total: int, report) -> str:
    pct = int((current / total) * 100)
    bar = "▓" * (pct // 5) + "░" * (20 - (pct // 5))
    
    return (
        f"<b>Verificando:</b> {current}/{total} ({pct}%)\n"
        f"<code>[{bar}]</code>\n"
        f"\n"
        f"<b>Validas:</b> {report.valid}\n"
        f"<b>Invalidas:</b> {report.invalid}\n"
        f"<b>Errores:</b> {report.errors}"
    )

def format_batch_report(report) -> str:
    valid_results = [r for r in report.results if r.status == "valid"]
    invalid_results = [r for r in report.results if r.status == "invalid"]
    error_results = [r for r in report.results if r.status == "error"]
    
    lines = [
        "<b>REPORTE FINAL</b>",
        "",
        f"<b>Total:</b> {report.total}",
        f"<b>Validas:</b> {report.valid}",
        f"<b>Invalidas:</b> {report.invalid}",
        f"<b>Errores:</b> {report.errors}",
        "",
    ]
    
    if valid_results:
        lines.append("<b>CUENTAS VALIDAS:</b>")
        for r in valid_results:
            exp = format_date(r.expiration) if r.expiration else "N/A"
            conn = r.connections or "?"
            lines.append(
                f"  ✅ <code>{r.username}</code> | {r.server} | "
                f"Exp: {exp} | Conn: {conn}"
            )
        lines.append("")
    
    if invalid_results:
        lines.append("<b>CUENTAS INVALIDAS:</b>")
        for r in invalid_results:
            lines.append(f"  ❌ <code>{r.username}</code> | {r.server}")
        lines.append("")
    
    if error_results:
        lines.append("<b>ERRORES:</b>")
        for r in error_results:
            lines.append(f"  ⚠️ <code>{r.username}</code> | {r.server} | {r.error}")
        lines.append("")
    
    return "\n".join(lines)
