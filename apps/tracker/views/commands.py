from aiogram import filters
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils import markdown

from apps.core.schemas import Observer
from apps.core.views import View
from apps.tracker.keyboards import TrackerCredentialsExistedSecretKeyboard
from apps.tracker.states import TrackerCreds
from apps.vault.services.secret import SecretService
from db.core import Session


class StartCommandView(View):
    observer = Observer(
        "message",
        [filters.Command("start")],
    )

    async def handle(self, message: Message):
        await message.answer(
            f"Привет, {markdown.bold(message.from_user.full_name)}\\!"
            + " Я помогу тебе пользоваться Яндекс Трекером голосом\\."
            + " Для начала использования тебе нужно ввести OAuth токен и Org\\-ID\\."
            + " Обещаю, что твои данные будут храниться в зашифрованном виде\\."
            + " Никто, кроме тебя, не сможет прочитать эти данные \\(даже админ\\)\\."
            + " Если ты хочешь начать пользоваться ботом, введи команду /login,"
            + " чтобы начать процесс связывания трекера с ботом\\."
        )


class AddTrackerCredentialsCommandView(View):
    observer = Observer(
        "message",
        [filters.Command("login")],
    )
    async def handle(self, message: Message, state: FSMContext, db_session: Session):
        service = SecretService(db_session)
        secret = service.get(message.from_user.id)

        if secret:
            await message.answer(
                "У тебя уже есть секрет с твоими данными\\. Нажми на кнопку, чтобы выбрать действие\\.",
                reply_markup=TrackerCredentialsExistedSecretKeyboard(),
            )
            await state.update_data(secret_id=secret.secret_id)
            await state.update_data(is_updating=True)
            return

        await state.set_state(TrackerCreds.token)
        await state.update_data(is_updating=False)
        await message.answer(
            "Давай начнём, сначала тебе нужно отправить мне свой OAuth токен от трекера\\."
            + " Не переживай, я его буду хранить всегда в зашифрованном виде\\."
        )
