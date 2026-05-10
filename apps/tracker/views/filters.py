from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from apps.account.models import User
from apps.ai.dialog import ApproveRequest
from apps.ai.integrations.yc.clients import McpClient
from apps.ai.integrations.yc.repositories import TrackerMcpRepository
from apps.core.schemas import Observer
from apps.core.views import View
from apps.tracker.ai import AITrackerHelper
from apps.vault.integrations.yc.repositories import TrackerSecretRepository, YCVaultClient
from db.core import Session
import settings

from ..keyboards import ConfirmMcpRequestKeyboard, TrackerCredentialsExistedSecretKeyboard
from ..states import TrackerCreds


class UpdateSecretTrackerFilterView(View):
    observer = Observer(
        "callback_query",
        [F.data == TrackerCredentialsExistedSecretKeyboard.UPDATE_DATA]
    )

    async def handle(self, callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        await callback.message.delete()
        await callback.message.answer(self.quote(
            "Давай начнём, сначала тебе нужно отправить мне свой OAuth токен от трекера.",
            "Не переживай, я его буду хранить всегда в зашифрованном виде.",
        ))
        await state.set_state(TrackerCreds.token)


class DeleteSecretTrackerFilterView(View):
    observer = Observer(
        "callback_query",
        [F.data == TrackerCredentialsExistedSecretKeyboard.DELETE_DATA]
    )

    async def _delete_secret(self, db_session: Session, user: User) -> bool:
        try:
            TrackerSecretRepository(YCVaultClient(settings.IAM_TOKEN), user.secret_id).delete()
        except Exception:
            return False
        else:
            user.secret_id = None
            db_session.commit()
            return True

    async def _delete_mcp(self, db_session: Session, user: User) -> bool:
        try:
            TrackerMcpRepository(McpClient(settings.IAM_TOKEN)).delete(user.mcp.mcp_gateway_id)
        except Exception:
            return False
        else:
            db_session.delete(user.mcp)
            db_session.commit()
            return True

    async def handle(self, callback: CallbackQuery, db_session: Session, user: User):
        await callback.message.delete()
        await callback.answer()
        if user.secret_id:
            deleted = await self._delete_secret(db_session, user)
            if deleted:
                await callback.message.answer(self.quote("Секрет успешно удалён."))
            else:
                await callback.message.answer(self.quote("Не удалось удалить секрет."))
        else:
            await callback.message.answer(self.quote("У тебя нет секрета."))

        if user.mcp:
            deleted = await self._delete_mcp(db_session, user)
            if deleted:
                await callback.message.answer(self.quote("MCP успешно удалён."))
            else:
                await callback.message.answer(self.quote("Не удалось удалить MCP."))
        else:
            await callback.message.answer(self.quote("У тебя нет MCP."))


class AIMessageFilterView(View):
    observer = Observer(
        "message",
        filters=[],
    )

    async def handle(self, message: Message, db_session: Session, user: User):
        if user.mcp is None or user.secret_id is None:
            return message.answer(self.quote(
                "Сначала тебе нужно добавить данные для авторизации в трекере.",
                "Используй команду /login",
                sep="\n",
            ))

        chat = AITrackerHelper(user, db_session)
        answer = chat.message(message.text)
        if isinstance(answer, list):
            return await message.answer(self.quote("Подтверди или отмени операцию, запрошенную ассистентом.\n\nКрасное - отменить\nЗелёное - подтвердить"), reply_markup=ConfirmMcpRequestKeyboard.build(answer))

        return await message.answer(self.quote(answer))


class SelectMcpRequestFilterView(View):
    observer = Observer(
        "callback_query",
        filters=[F.data.startswith(ConfirmMcpRequestKeyboard.SELECT_BUTTON_PREFIX)],
    )

    async def handle(self, callback: CallbackQuery):
        await callback.answer()
        buttons = callback.message.reply_markup.inline_keyboard
        for row in buttons:
            for button in row:
                if button.callback_data == callback.data:
                    button.style = "danger" if button.style == "success" else "success"

        await callback.bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=callback.message.reply_markup)


class ConfirmMcpRequestFilterView(View):
    observer = Observer(
        "callback_query",
        filters=[F.data == ConfirmMcpRequestKeyboard.CONFIRM],
    )

    async def handle(self, callback: CallbackQuery, db_session: Session, user: User):
        await callback.answer()
        await callback.message.delete()
        buttons = callback.message.reply_markup.inline_keyboard
        approves = []
        for row in buttons:
            for button in row:
                if button.callback_data.startswith(ConfirmMcpRequestKeyboard.SELECT_BUTTON_PREFIX):
                    request_id = button.callback_data.removeprefix(ConfirmMcpRequestKeyboard.SELECT_BUTTON_PREFIX)
                    approves.append(ApproveRequest(id=request_id, approve=button.style == "success"))

        chat = AITrackerHelper(user, db_session)
        answer = chat.approve_requests(approves)
        if isinstance(answer, list):
            return await callback.message.answer(self.quote("Подтверди или отмени операцию, запрошенную ассистентом.\n\nКрасное - отменить\nЗелёное - подтвердить)"), reply_markup=ConfirmMcpRequestKeyboard.build(answer))

        return await callback.message.answer(self.quote(answer))
