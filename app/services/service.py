import httpx
import logging
from typing import Optional

from app.core.http_client import HttpClient
from app.core.exceptions import (
    XtreamError,
    InvalidCredentialsError,
    ServerNotRespondingError
)
from app.models.xtream_dto import XtreamResponseDTO
from app.models.request_dto import XtreamRequestDTO

logger = logging.getLogger(__name__)

class XtreamService:
    def __init__(self):
        self.http = HttpClient()
        
    async def check_account(self, data: XtreamRequestDTO) -> XtreamResponseDTO:
        """
        Flujo completo:
        1. Construir URL
        2. Llamar API
        3. Validar respuesta
        4. Convertir a DTO
        """
        
        url = self._build_url(data)
        
        try: 
            raw = await self.http.get(url)
            
        except httpx.ConnectTimeout as e:
            
            logger.exception(
                f"[XTREAM] ConnectTimeout -> {repr(e)}"
            )
            
            raise ServerNotRespondingError(
                "Timeout conectando al servidor"
            )
        except httpx.ReadTimeout as e:
            
            logger.exception(
                f"[XTREAM] ReadTimeout -> {repr(e)}"
            )
            
            raise ServerNotRespondingError(
                "El servidor tardo demasiado en responder"
            )
            
        except httpx.ConnectError as e:
            
            logger.exception(
                f"[XTREAM] ConnectError -> {repr(e)}"
            )
            
            raise XtreamError(
                f"HTTP Error: {e.response.status_code}"
            )
            
        except Exception as e:
            logger.exception(
                f"[XTREAM] Unknown Error -> {repr(e)}"
            )
            
            raise ServerNotRespondingError(
                "Error desconocido del servidor"
            )
        
        # Validar respuesta vacia o invalida
        if not raw or "user_info" not in raw:
            raise XtreamError("Respuesta invalida del servidor")
        
        # Validar autenticacion
        if not self._is_authenticated(raw):
            raise InvalidCredentialsError("Credenciales invalidas")
        
        # Convertir a DTO (tipado fuerte)
        try:
            parsed = XtreamResponseDTO(**raw)
        except Exception as e:
            logger.error(f"[XTREAM] Error parsing DTO: {str(e)}")
            raise XtreamError("Error parseando respuesta")
        
        return parsed
    
    # =======================
    # 🔧 METODOS INTERNOS
    # =======================
    
    def _build_url(self, data: XtreamRequestDTO) -> str:
        """
        Construye endpoint
        """
        server = str(data.server).rstrip("/")
        
        return f"{server}/player_api.php?username={data.username}&password={data.password}"
    
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
        """
        Convierte DTO en respuesta simplificada
        (lo que usara telegram)
        """
        
        user = dto.user_info
        server = dto.server_info
        
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
        
    def _safe_int(self, value: Optional[str]) -> Optional[int]:
        try:
            return int(value) if value else None
        except:
            return None
        
        
        
    
        