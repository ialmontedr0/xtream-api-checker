from pydantic import BaseModel
from typing import Optional

class XtreamUserInfo(BaseModel):
    username: Optional[str] = None
    status: Optional[str] = None
    exp_date: Optional[int] = None
    is_trial: Optional[str] = None
    active_cons: Optional[int] = None
    created_at: Optional[int] = None
    max_connections: Optional[int] = None

class XtreamServerInfo(BaseModel):
    url: Optional[str] = None
    port: Optional[str] = None
    timezone: Optional[str] = None

class XtreamResponseDTO(BaseModel):
    user_info: Optional[XtreamUserInfo] = None
    server_info: Optional[XtreamServerInfo] = None
