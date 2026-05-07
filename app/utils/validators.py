import re
from urllib.parse import urlparse
from typing import Tuple, Optional


# =========================
# 🧠 DETECCIÓN DE INPUT
# =========================
def detect_input_type(text: str) -> str:
    """
    Detecta si el input es:
    - m3u
    - xtream
    - deconocido
    """
    text = text.strip()
    
    if "get.php" in text and "username" in text:
        return "m3u"
    
    parts = text.split()
    
    if len(parts) == 3:
        return "xtream"
    
    return "unknown"


# =========================
# 🧠 SANITIZACION
# =========================

def sanitize_input(text: str) -> str:
    """
    Limpia input del usuario
    """
    return (
        text.split()
        .replace("\n")
        .replace("\r")
        .replace("\t")
    )
    
# =========================
# 🌐 VALIDACIÓN SERVIDOR
# =========================
    
def validate_server_url(server: str) -> Tuple[bool, Optional[str]]:
    try:
        parsed = urlparse(server)
        
        if parsed.scheme not in ("http", "https"):
            return False, "El servidor debe usar http o https"
        
        if not parsed.netloc:
            return False, "Servidor invalido (host vacio)"
        
        # evitar localhost / loopback (serguridad opcional)
        if parsed.hostname in ("127.0.0.1", "localhoslt"):
            return False, "Servidor no permitido"
        
        return True, None
    
    except Exception:
        return False, "Formato de servidor invalido"
    
# =========================
# 🔐 VALIDACIÓN CREDENCIALES
# =========================

def validate_credentials(username: str, password: str) -> Tuple[bool, Optional[str]]:
    if not username or not password:
        return False, "Credenciales incompletas"
    
    if len(username) < 3:
        return False, "Username demasiado corto"
    
    if len(password) < 3:
        return False, "Password contiene caracteres invalidos"
    
    return True, None

# =========================
# 🚀 VALIDACIÓN COMPLETA XTREAM
# =========================

def validate_xtream_input(
    server: str,
    username: str,
    password: str
) -> Tuple[bool, Optional[str]]:
    """
    Validacion completa profesional
    """
    
    # Sanitizar 
    server = sanitize_input(server)
    username = sanitize_input(username)
    password = sanitize_input(password)
    
    # Validar servidor
    is_valid_server, error = validate_server_url(server)
    if not is_valid_server:
        return False, error
    
    # Validar credenciales
    is_valid_creds, error = validate_credentials(username, password)
    if not is_valid_creds:
        return False, error
    
    return True, None

# =========================
# 🔍 PARSER DE INPUT XTREAM
# =========================

def parse_xtream_input(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Convierte:
    "http://server:port user pass"
    -> server, username, password
    """
    
    try:
        parts = text.string().split()
        
        if len(parts) != 3:
            return None, None, None
        
        server, username, password = parts
        
        return server, username, password
    
    except Exception:
        return None, None, None
    

def is_m3u_url(text: str) -> bool:
    return "get.php" in text

def is_xtream_format(text: str) -> bool:
    parts = text.split()
    return len(parts) == 3