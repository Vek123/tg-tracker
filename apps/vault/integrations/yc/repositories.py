from dataclasses import dataclass
from typing import Self

from requests import HTTPError

import settings

from apps.vault.integrations.yc.clients import YCVaultClient

from .schemas import Payload, SecretCreateData, SecretUpdateVersionData


@dataclass
class TrackerData:
    org_id: int | None = None
    token: str | None = None


class TrackerSecretRepository:
    secret_name_template = "tracker_{user_id}"
    token_key_field = "token"
    org_id_key_field = "org-id"

    def __init__(self, client: YCVaultClient, secret_id: str):
        self.secret_id = secret_id
        self.client = client

    @classmethod
    def create(cls, client: YCVaultClient, data: TrackerData | None, user_id: int | None) -> Self:
        payloads = []
        if data.org_id:
            payloads.append(Payload(key=cls.org_id_key_field, text_value=str(data.org_id)))

        if data.token:
            payloads.append(Payload(key=cls.token_key_field, text_value=data.token))
    
        secret = client.secret.create(
            SecretCreateData(
                folder_id=settings.YC_FOLDER_ID,
                name=cls.secret_name(user_id),
                version_payload_entries=payloads,
            )
        )
        secret_id = secret.metadata.secret_id
        return cls(client=client, secret_id=secret_id)

    @classmethod
    def get(cls, client: YCVaultClient, secret_id: str) -> Self | None:
        try:
            client.secret.get(secret_id)
        except HTTPError:
            return

        return cls(client, secret_id)

    @classmethod
    def secret_name(cls, user_id: int) -> str:
        return cls.secret_name_template.format(user_id=user_id)

    def delete(self) -> None:
        try:
            self.client.secret.delete(self.secret_id)
        except HTTPError:
            pass

    def get_payload(self) -> TrackerData:
        payloads = self.client.payload.get(self.secret_id)
        token = None
        org_id = None
        for payload in payloads:
            if payload.key == self.token_key_field:
                token = payload.text_value
            elif payload.key == self.org_id_key_field:
                org_id = int(payload.text_value)

        return TrackerData(org_id=org_id, token=token)

    def update(self, token: str | None = None, org_id: int | None = None) -> None:
        payloads = []
        if org_id:
            payloads.append(Payload(key=self.org_id_key_field, text_value=str(org_id)))

        if token:
            payloads.append(Payload(key=self.token_key_field, text_value=token))

        data = SecretUpdateVersionData(
            payloadEntries=payloads,
        )
        self.client.secret.update_version(
            self.secret_id,
            data,
        )
