import logging
from urllib.parse import urlparse, parse_qs
from typing import Dict, Optional

from app.core.exceptions import XtreamError

logger = logging.getLogger(__name__)

class M3UParser:
    
    def parse(self, m3u_url: str) -> Dict[str, str]:
        """
        Convierte URL M3U -> credenciales Xtream
        
        Retorna:
        {
            server: str,
            username: str,
            password: str
        }
        """
        
        if not m3u_url:
            raise XtreamError("URL M3U vacia")
        
        clean_url = self._sanitize(m3u_url)
        
        parsed = urlparse(clean_url)
        
        if not parsed.scheme or not parsed.netloc:
            raise XtreamError("URL invalida")
        
        query = self._extract_query(parsed)
        
        username = query.get("username")
        password = query.get("password")
        
        self._validate(username, password)
        
        server = self._build_server(parsed)
        
        return {
            "server": server,
            "username": username,
            "password": password
        }
        
    # =========================
    # 🔧 MÉTODOS INTERNOS
    # =========================
    
    def _sanitize(self, url: str) -> str:
        """
        Limpia espacios, saltos de linea, etc
        """
        return url.strip().replace("\n", "").replace("\r", "")
    
    def _extract_query(self, parsed) -> Dict[str, Optional[str]]:
        """
        Extrae query params de forma segura
        """
        try:
            query_dict = parse_qs(parsed.query, keep_blank_values=True)
            
            return {
                "username": query_dict.get("username", [None])[0],
                "password": query_dict.get("password", [None])[0]
            }
            
        except Exception as e:
            logger.error(f"[M3U] Error parsing query: {str(e)}")
            raise XtreamError("Error leyendo parametros M3U")
        
    def _validate(self, username: Optional[str], password: Optional[str]):
        """
        Validacion estricta
        """
        if not username:
            raise XtreamError("M3U sin username")
        
        if not password:
            raise XtreamError("M3U sin contrasena")
        
        if len(username) < 3:
            raise XtreamError("Username invalido")
        
        if len(password) < 3:
            raise XtreamError("Contrasena invalida")
        
    
    def _build_server(self, parsed) -> str:
        """
        Reconstruye servidor base
        """
        scheme = parsed.scheme
        netloc = parsed.netloc
        
        return f"{scheme}://{netloc}"
    
    # =========================
    # 🧠 FUNCIONES AVANZADAS
    # =========================
    
    def is_m3u(self, text: str) -> bool:
        """
        Detecta si el input es M3U
        """
        return "get.php" in text and "username" in text
    
    def safe_parse(self, m3u_url: str) -> Optional[Dict[str, str]]:
        """
        Parseo seguro (no rompe flujo)
        """
        try:
            return self.parse(m3u_url)
        except Exception as e:
            logger.warning(f"[M3U] Parse fallido: {str(e)}")
            return None        