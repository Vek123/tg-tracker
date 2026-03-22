from aiogram.types.inline_keyboard_button import InlineKeyboardButton

from apps.core.keyboards import InlineKeyboard


class TrackerCredentialsExistedSecretKeyboard(InlineKeyboard):
    UPDATE_DATA = "login_existed_secret_update_data"
    DELETE_DATA = "login_existed_secret_delete_data"
    markup = [
        [InlineKeyboardButton(text="Обновить", callback_data=UPDATE_DATA), InlineKeyboardButton(text="Удалить", callback_data=DELETE_DATA)],
    ]
