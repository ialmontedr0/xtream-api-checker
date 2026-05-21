import asyncio
import logging
from typing import Optional
from urllib.parse import quote

from app.core.http_client import HttpClient
from app.core.exceptions import (
    XtreamError,
    InvalidCredentialsError,
    ServerNotRespondingError
)
from app.models.xtream_dto import XtreamResponseDTO, XtreamUserInfo, XtreamServerInfo
from app.models.request_dto import XtreamRequestDTO

logger = logging.getLogger(__name__)

SPANISH_KEYWORDS = [
    "español", "espanol", "spanish", "latino", "hispano",
    "méxico", "mexico", "argentina", "colombia", "chile",
    "perú", "peru", "venezuela", "ecuador", "cuba", "bolivia",
    "uruguay", "paraguay", "guatemala", "honduras",
    "nicaragua", "panamá", "panama", "costa rica",
    "puerto rico", "república dominicana", "republica dominicana",
    "telenovela", "castellano",
    "españa", "spain", "latin", "américa latina", "america latina",
    "sudamerica", "suramerica", "centroamerica",
    "el salvador"
]

class XtreamService:
    def __init__(self):
        self.http = HttpClient()
        
    async def check_account(self, data: XtreamRequestDTO) -> XtreamResponseDTO:
        
        url = self._build_url(data)
        
        logger.info(f"[XTREAM] URL: {url}")
        
        try: 
            raw = await self.http.get(url)
            
        except Exception as e:
            logger.error(f"[XTREAM] Error HTTP: {str(e)}")
            raise ServerNotRespondingError("Servidor no responde")
        
        if not raw or "user_info" not in raw:
            raise XtreamError("Respuesta invalida del servidor")
        
        if not self._is_authenticated(raw):
            raise InvalidCredentialsError("Credenciales invalidas")
        
        try:
            parsed = XtreamResponseDTO(**raw)
        except Exception as e:
            logger.error(f"[XTREAM] Error parsing DTO: {str(e)}")
            raise XtreamError("Error parseando respuesta")
        
        return parsed
    
    def _build_url(self, data: XtreamRequestDTO) -> str:
        return self._build_base_url(data)

    def _build_base_url(self, data: XtreamRequestDTO) -> str:
        server = str(data.server).rstrip("/")
        username = quote(data.username, safe="")
        password = quote(data.password, safe="")
        return f"{server}/player_api.php?username={username}&password={password}"
    
    def _is_authenticated(self, response: dict) -> bool:
        """
        Valida si la cuenta en valida segun API Xtream
        """
        user_info = response.get("user_info", {})
        
        # auth = 1 -> valido
        if user_info.get("auth") == 1:
            return True
        
        # fallback por status
        status = user_info.get("status", "").lower()
        
        if status == "active":
            return True
        
        return False
    
    # =======================
    # 🧠 HELPERS AVANZADOS
    # =======================
    
    def extract_summary(self, dto: XtreamResponseDTO) -> dict:
        user = dto.user_info or XtreamUserInfo()
        server = dto.server_info or XtreamServerInfo()
        
        return {
            "username": user.username,
            "status": user.status,
            "created_at": self._safe_int(user.created_at),
            "expiration": self._safe_int(user.exp_date),
            "active_connections": self._safe_int(user.active_cons),
            "max_connections": self._safe_int(user.max_connections),
            "timezone": server.timezone,
            "server_url": server.url
        }
        
    def _safe_int(self, value) -> Optional[int]:
        try:
            return int(value) if value else None
        except:
            return None

    # =======================
    # 🌎 DETECCION DE CONTENIDO LATINO
    # =======================

    def _matches_spanish(self, text: Optional[str]) -> bool:
        if not text:
            return False
        t = text.lower()
        return any(kw in t for kw in SPANISH_KEYWORDS)

    def _extract_list(self, response, *keys):
        if isinstance(response, list):
            return response
        for key in keys:
            if isinstance(response, dict):
                val = response.get(key)
                if isinstance(val, list):
                    return val
        return []

    async def _fetch_json(self, url: str):
        try:
            return await self.http.get(url)
        except Exception as e:
            logger.warning(f"[CONTENT] Error fetching {url}: {e}")
            return None

    async def check_spanish_content(self, data: XtreamRequestDTO) -> dict:
        base = self._build_base_url(data)

        result = {
            "channels": {"has": False, "count": 0, "total": 0},
            "movies": {"has": False, "count": 0, "total": 0},
            "series": {"has": False, "count": 0, "total": 0},
        }

        async def check_live():
            try:
                cat_raw = await self._fetch_json(f"{base}&action=get_live_categories")
                if cat_raw is None:
                    return
                cats = self._extract_list(cat_raw, "categories")
                spanish_cat_ids = set()
                for c in cats:
                    if self._matches_spanish(c.get("category_name", "")):
                        cid = c.get("category_id")
                        if cid:
                            spanish_cat_ids.add(str(cid))

                streams_raw = await self._fetch_json(f"{base}&action=get_live_streams")
                if streams_raw is None:
                    result["channels"]["has"] = len(spanish_cat_ids) > 0
                    return

                streams = self._extract_list(streams_raw, "live_streams", "streams")
                count = 0
                for s in streams:
                    cid = str(s.get("category_id", ""))
                    if cid in spanish_cat_ids or self._matches_spanish(s.get("name", "")):
                        count += 1

                result["channels"]["has"] = count > 0
                result["channels"]["count"] = count
                result["channels"]["total"] = len(streams)
            except Exception as e:
                logger.warning(f"[CONTENT] Error checking live: {e}")

        async def check_vod():
            try:
                cat_raw = await self._fetch_json(f"{base}&action=get_vod_categories")
                if cat_raw is None:
                    return
                cats = self._extract_list(cat_raw, "categories")
                spanish_cat_ids = set()
                for c in cats:
                    if self._matches_spanish(c.get("category_name", "")):
                        cid = c.get("category_id")
                        if cid:
                            spanish_cat_ids.add(str(cid))

                vod_raw = await self._fetch_json(f"{base}&action=get_vod_streams")
                if vod_raw is None:
                    result["movies"]["has"] = len(spanish_cat_ids) > 0
                    return

                vods = self._extract_list(vod_raw, "vod_streams", "streams", "movies")
                count = 0
                for v in vods:
                    cid = str(v.get("category_id", ""))
                    if cid in spanish_cat_ids or self._matches_spanish(v.get("name", "")):
                        count += 1

                result["movies"]["has"] = count > 0
                result["movies"]["count"] = count
                result["movies"]["total"] = len(vods)
            except Exception as e:
                logger.warning(f"[CONTENT] Error checking vod: {e}")

        async def check_series():
            try:
                cat_raw = await self._fetch_json(f"{base}&action=get_series_categories")
                if cat_raw is None:
                    return
                cats = self._extract_list(cat_raw, "categories")
                spanish_cat_ids = set()
                for c in cats:
                    if self._matches_spanish(c.get("category_name", "")):
                        cid = c.get("category_id")
                        if cid:
                            spanish_cat_ids.add(str(cid))

                series_raw = await self._fetch_json(f"{base}&action=get_series")
                if series_raw is None:
                    result["series"]["has"] = len(spanish_cat_ids) > 0
                    return

                series_list = self._extract_list(series_raw, "series")
                count = 0
                for s in series_list:
                    cid = str(s.get("category_id", ""))
                    if cid in spanish_cat_ids or self._matches_spanish(s.get("name", "")):
                        count += 1

                result["series"]["has"] = count > 0
                result["series"]["count"] = count
                result["series"]["total"] = len(series_list)
            except Exception as e:
                logger.warning(f"[CONTENT] Error checking series: {e}")

        await asyncio.gather(check_live(), check_vod(), check_series())

        return result
        
        
        
    
        