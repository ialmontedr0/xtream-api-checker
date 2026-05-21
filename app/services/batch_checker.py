import asyncio
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from app.models.request_dto import XtreamRequestDTO
from app.core.exceptions import InvalidCredentialsError, ServerNotRespondingError, XtreamError
from app.services.xtream import XtreamService

logger = logging.getLogger(__name__)

@dataclass
class BatchResult:
    username: str
    server: str
    status: str = "pending"
    expiration: Optional[str] = None
    connections: Optional[str] = None
    error: Optional[str] = None

@dataclass
class BatchReport:
    total: int = 0
    valid: int = 0
    invalid: int = 0
    errors: int = 0
    results: List[BatchResult] = field(default_factory=list)

class BatchChecker:
    def __init__(self):
        self.service = XtreamService()

    async def check_list(
        self,
        entries: List[Dict[str, str]],
        progress_callback=None
    ) -> BatchReport:
        
        report = BatchReport(total=len(entries))
        
        for i, entry in enumerate(entries, 1):
            dto = XtreamRequestDTO(
                server=entry["server"],
                username=entry["username"],
                password=entry["password"]
            )
            
            result = await self._check_single(dto)
            report.results.append(result)
            
            if result.status == "valid":
                report.valid += 1
            elif result.status == "invalid":
                report.invalid += 1
            else:
                report.errors += 1
            
            if progress_callback:
                await progress_callback(i, len(entries), report)
            
            await asyncio.sleep(1.0)
        
        return report
    
    async def _check_single(self, dto: XtreamRequestDTO) -> BatchResult:
        result = BatchResult(username=dto.username, server=dto.server)
        
        try:
            response = await self.service.check_account(dto)
            summary = self.service.extract_summary(response)
            
            result.status = "valid"
            result.expiration = summary.get("expiration")
            
            active = summary.get("active_connections", "?")
            max_conn = summary.get("max_connections", "?")
            result.connections = f"{active}/{max_conn}"
            
            return result
            
        except InvalidCredentialsError:
            result.status = "invalid"
            result.error = "Credenciales invalidas"
            return result
            
        except ServerNotRespondingError:
            result.status = "error"
            result.error = "Servidor no responde"
            return result
            
        except Exception as e:
            result.status = "error"
            result.error = str(e)
            return result
