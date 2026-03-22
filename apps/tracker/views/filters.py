from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from apps.core.schemas import Observer
from apps.core.views import View
from apps.vault.integrations.yc.repositories import TrackerSecretRepository, YCVaultClient
from apps.vault.services.secret import SecretService
from db.core import Session
import settings

from ..keyboards import TrackerCredentialsExistedSecretKeyboard
from ..states import TrackerCreds


class UpdateSecretTrackerFilterView(View):
    observer = Observer(
        "callback_query",
        [F.data == TrackerCredentialsExistedSecretKeyboard.UPDATE_DATA]
    )

    async def handle(self, callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        await callback.message.answer(
            "Давай начнём, сначала тебе нужно отправить мне свой OAuth токен от трекера\\."
            + " Не переживай, я его буду хранить всегда в зашифрованном виде\\."
        )
        await state.set_state(TrackerCreds.token)


class DeleteSecretTrackerFilterView(View):
    observer = Observer(
        "callback_query",
        [F.data == TrackerCredentialsExistedSecretKeyboard.DELETE_DATA]
    )

    async def handle(self, callback: CallbackQuery, db_session: Session, vault):
        service = SecretService(db_session)
        secret = service.get(callback.message.from_user.id)
        TrackerSecretRepository(YCVaultClient(settings.IAM_TOKEN), secret.secret_id).delete()
        service.delete(callback.message.from_user.id)

        await callback.answer()
        await callback.message.answer("Секрет успешно удалён\\.")

