from pydantic import BaseModel

class XtreamRequestDTO(BaseModel):
    server: str
    username: str
    password: str