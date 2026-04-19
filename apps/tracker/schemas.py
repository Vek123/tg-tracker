from dataclasses import dataclass


@dataclass
class TrackerData:
    org_id: int | None = None
    token: str | None = None
