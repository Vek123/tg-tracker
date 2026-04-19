from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from apps.account.models import User
from apps.ai.dialog import Chat
from apps.ai.integrations.yc.tools.tracker import get_personal_use_tools
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
        await callback.message.delete()
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

    async def handle(self, callback: CallbackQuery, db_session: Session):
        service = SecretService(db_session)
        secret = service.get(callback.from_user.id)
        TrackerSecretRepository(YCVaultClient(settings.IAM_TOKEN), secret.secret_id).delete()
        service.delete(callback.from_user.id)

        await callback.message.delete()
        await callback.answer()
        await callback.message.answer("Секрет успешно удалён\\.")


class AIMessageFilterView(View):
    observer = Observer(
        "message",
        filters=[],
    )

    async def handle(self, message: Message, db_session: Session, user: User):
        if user.mcp is None:
            return message.answer((
                "Сначала тебе нужно добавить данные для авторизации в трекере\\.\n"
                "Используй команду /login"
            ))

        chat = Chat(
            model_url=settings.YC_AI_MODEL_URL,
            tools=get_personal_use_tools(user.mcp.mcp_base_url)
        )
        answer = chat.message(message.text)
        return await message.answer(answer)
