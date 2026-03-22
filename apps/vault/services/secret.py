from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from apps.vault import models


class SecretService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, user_id: int) -> models.Secret | None:
        query = select(models.Secret).where(models.Secret.user_id == user_id)
        return self.session.execute(query).scalar_one_or_none()

    def get_user(self, secret_id: str) -> models.Secret | None:
        query = select(models.Secret).where(models.Secret.secret_id == secret_id)
        return self.session.execute(query).scalar_one_or_none()

    def create(self, user_id: int, secret_id: str) -> models.Secret:
        secret = models.Secret(user_id=user_id, secret_id=secret_id)
        self.session.add(secret)
        self.session.commit()
        return secret

    def create_or_update(self, user_id: int, secret_id: str) -> models.Secret:
        created, instance = self.get_or_create(user_id, secret_id)
        if not created:
            instance.secret_id = secret_id
            self.session.commit()

        return instance

    def get_or_create(self, user_id: int, secret_id: str) -> tuple[bool, models.Secret]:
        created = True
        if secret := self.get(user_id):
            created = False
            return secret

        return created, self.create(user_id, secret_id)

    def update(self, user_id: int, secret_id: str) -> models.Secret | None:
        secret = self.session.get(models.Secret, user_id)
        if not secret:
            return

        secret.secret_id = secret_id
        self.session.commit()
        return secret

    def delete(self, user_id: int) -> None:
        stmt = delete(models.Secret).where(models.Secret.user_id == user_id)
        self.session.execute(stmt)
        self.session.commit()
