from dataclasses import dataclass
import datetime


@dataclass(frozen=True)
class SAKey:
    id: str
    service_account_id: str
    created_at: datetime.datetime
    key_algorithm: str
    public_key: str
    private_key: str
