from pydantic import BaseModel
from typing import Optional

class XtreamUserInfo(BaseModel):
    username: Optional[str]
    status: Optional[str]
    exp_date: Optional[int]
    is_trial: Optional[str]
    active_cons: Optional[int]
    created_at: Optional[int]
    max_connections: Optional[int]
    
class XtreamServerInfo(BaseModel):
    url: Optional[str]
    port: Optional[str]
    timezone: Optional[str]
    
class XtreamResponseDTO(BaseModel):
    user_info: XtreamUserInfo
    server_info: XtreamServerInfo