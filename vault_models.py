from dataclasses import dataclass

import settings
from vault import Payload, SecretCreateData, SecretUpdateData, YCPayloadService, YCVaultService


@dataclass
class TrackerData:
    org_id: int
    token: int


class Tracker:
    name_template = "tracker_{user_id}"
    token_key_field = "token"
    org_id_key_field = "org-id"

    def __init__(self, service: YCVaultService, secret_id: str):
        self.secret_id = secret_id
        self.service = service

    @classmethod
    def create(cls, service: YCVaultService, user_id: int, token: str | None = None, org_id: int | None = None) -> "Tracker":
        payloads = []
        if token:
            payloads.append(
                Payload(
                    key=cls.token_key_field,
                    text_value=str(user_id),
                )
            )

        if org_id:
            payloads.append(
                Payload(
                    key=cls.org_id_key_field,
                    text_value=str(org_id)
                )
            )

        secret = service.secret.create(
            SecretCreateData(
                folder_id=settings.YC_FOLDER_ID,
                name=cls.name_template.format(user_id=user_id),
                version_payload_entries=payloads,
            )
        )
        secret_id = secret.metadata.secret_id
        return cls(service=service, secret_id=secret_id)

    def delete(self) -> None:
        self.service.secret.delete(self.secret_id)

    def get(self) -> TrackerData:
        payloads = self.service.payload.get(self.secret_id)
        token = None
        org_id = None
        for payload in payloads:
            if payload.key == self.token_key_field:
                token = int(payload.text_value)
            elif payload.key == self.org_id_key_field:
                org_id = int(payload.text_value)

        return TrackerData(org_id=org_id, token=token)

    def update(self, data: TrackerData) -> None:
        payloads = [
            Payload(
                key=
            )
        ]
        data = SecretUpdateData(
            
        )
        self.service.secret.update(
            self.secret_id,
            
        )
