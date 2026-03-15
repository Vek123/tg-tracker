from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class Keyboard:
    def __new__(cls):
        return cls.builder(cls.markup).as_markup()


class ReplyKeyboard(Keyboard):
    builder = ReplyKeyboardBuilder


class InlineKeyboard(Keyboard):
    builder = InlineKeyboardBuilder


class LoginCommandExistedSecretKeyboard(InlineKeyboard):
    UPDATE_DATA = "login_existed_secret_update_data"
    DELETE_DATA = "login_existed_secret_delete_data"
    markup = [
        [InlineKeyboardButton(text="Обновить", callback_data=UPDATE_DATA), InlineKeyboardButton(text="Удалить", callback_data=DELETE_DATA)],
    ]
