from aiogram import F, Router, filters
from aiogram.types import CallbackQuery, Message
from aiogram.utils import markdown
from aiogram.fsm.context import FSMContext

from db import get_session
from keyboards import LoginCommandExistedSecretKeyboard
from services import SecretService
from states import TrackerCreds
from vault import YCVaultService

router = Router()

@router.message(filters.CommandStart())
async def command_start_handler(message: Message):
    """
    /start
    """
    await message.answer(
        f"Привет, {markdown.bold(message.from_user.full_name)}\\!"
        + " Я помогу тебе пользоваться Яндекс Трекером голосом\\."
        + " Для начала использования тебе нужно ввести OAuth токен и Org\\-ID\\."
        + " Обещаю, что твои данные будут храниться в зашифрованном виде\\."
        + " Никто, кроме тебя, не сможет прочитать эти данные \\(даже админ\\)\\."
        + " Если ты хочешь начать пользоваться ботом, введи команду /login,"
        + " чтобы начать процесс связывания трекера с ботом\\."
    )


@router.message(filters.Command("login"))
async def command_login_handler(message: Message, state: FSMContext):
    """
    /login
    """
    with get_session() as session:
        service = SecretService(session)
        secret = service.get(message.from_user.id)

    if secret:
        await message.answer(
            "У тебя уже есть секрет с твоими данными\\. Нажми на кнопку, чтобы выбрать действие\\.",
            reply_markup=LoginCommandExistedSecretKeyboard(),
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


@router.callback_query(F.data == LoginCommandExistedSecretKeyboard.UPDATE_DATA)
async def update_secret(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "Давай начнём, сначала тебе нужно отправить мне свой OAuth токен от трекера\\."
        + " Не переживай, я его буду хранить всегда в зашифрованном виде\\."
    )
    await state.set_state(TrackerCreds.token)


@router.callback_query(F.data == LoginCommandExistedSecretKeyboard.DELETE_DATA)
async def delete_secret(callback: CallbackQuery, state: FSMContext, vault: YCVaultService):
    with get_session() as session:
        service = SecretService(session)
        secret = service.get(callback.message.from_user.id)
        vault.secret.delete(secret.secret_id)
        service.delete(callback.message.from_user.id)

    await callback.answer()
    await callback.message.answer("Секрет успешно удалён\\.")


@router.message(TrackerCreds.token)
async def process_token(message: Message, state: FSMContext, vault: YCVaultService):
    token = message.text
    data = await state.get_data()
    if data["is_updating"]:
        secret_id = data["secret_id"]
        vault.secret.update(
            secret_id,
            
        )

    await state.set_state(TrackerCreds.org_id)
    await message.answer(
        "Теперь мне нужен Org\\-ID\\."
    )


@router.message(TrackerCreds.org_id)
async def process_org_id(message: Message, state: FSMContext, vault: YCVaultService):
    await state.update_data(org_id=message.text)
    data = await state.get_data()
    with get_session() as session:
        service = SecretService(session)
        service.create_or_update(message.from_user.id, f"{data["token"]}:{data["org_id"]}")

    await state.clear()
    await message.answer(
        f"Хорошо, твои данные: {data["token"]}, {data["org_id"]}\\."
    )
