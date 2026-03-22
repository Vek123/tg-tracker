from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from apps.core.schemas import Observer
from apps.core.views import View
from apps.vault.integrations.yc.repositories import TrackerSecretRepository, YCVaultClient, TrackerData
from apps.vault.services.secret import SecretService
from db.core import Session
import settings

from ..keyboards import TrackerCredentialsExistedSecretKeyboard
from ..states import TrackerCreds


class UpdateSecretTrackerStateView(View):
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


class ProcessTrackerTokenStateView(View):
    observer = Observer(
        "message",
        [TrackerCreds.token],
    )

    async def handle(self, message: Message, state: FSMContext, db_session: Session):
        token = message.text
        data = await state.get_data()
        client = YCVaultClient(settings.IAM_TOKEN)
        if data["is_updating"]:
            tracker_repo = TrackerSecretRepository(client, data["secret_id"])
            tracker_repo.update(token=token)
        else:
            tracker_repo = TrackerSecretRepository.create(client, TrackerData(token=token), message.from_user.id)
            await state.update_data(secret_id=tracker_repo.secret_id)
            SecretService(db_session).create(
                user_id=message.from_user.id,
                secret_id=tracker_repo.secret_id,
            )

        await state.set_state(TrackerCreds.org_id)
        await message.answer(
            "Теперь мне нужен Org\\-ID\\."
        )


class ProcessTrackerOrgIdStateView(View):
    observer = Observer(
        "message",
        [TrackerCreds.org_id],
    )

    async def handle(self, message: Message, state: FSMContext, db_session: Session):
        org_id = message.text
        data = await state.get_data()

        TrackerSecretRepository(YCVaultClient(settings.IAM_TOKEN), data["secret_id"]).update(org_id=org_id)

        await state.clear()
        await message.answer(
            f"Хорошо, мы записали твои данные в секрет: {data['secret_id']}"
        )
