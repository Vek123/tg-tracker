from aiogram import Router, filters
from aiogram.types import Message
from aiogram.utils import markdown
from aiogram.fsm.context import FSMContext

from states import TrackerCreds

router = Router()

@router.message(filters.CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    """
    /start
    """
    await message.answer(
        f"""Привет, {markdown.bold(message.from_user.full_name)}!
        Я помогу тебе пользоваться Яндекс Трекером голосом.
        Для начала использования тебе нужно ввести OAuth токен и Org-ID.
        Обещаю, что твои данные будут храниться в зашифрованном виде.
        Никто, кроме тебя, не сможет прочитать эти данные (даже админ).
        Если ты хочешь начать пользоваться ботом, введи команду /login,
        чтобы начать процесс связывания трекера с ботом."""
    )


@router.message(filters.Command("login"))
async def command_login_handler(message: Message, state: FSMContext):
    """
    /login
    """
    await state.set_state(TrackerCreds.token)
    await message.answer(
        """Давай начнём, сначала тебе нужно отправить мне свой OAuth токен от трекера.
        Не переживай, я его буду хранить всегда в зашифрованном виде."""
    )


@router.message(TrackerCreds.token)
async def process_token(message: Message, state: FSMContext):
    await state.update_data(token=message.text)
    await state.set_state(TrackerCreds.org_id)
    await message.answer(
        """Теперь мне нужен Org-ID."""
    )


@router.message(TrackerCreds.org_id)
async def process_org_id(message: Message, state: FSMContext):
    await state.update_data(org_id=message.text)
    data = await state.get_data()
    await state.clear()
    message.answer(
        f"""Хорошо, твои данные: {data["token"]}, {data["org_id"]}"""
    )
