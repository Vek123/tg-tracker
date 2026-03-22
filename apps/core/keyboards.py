from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class Keyboard:
    def __new__(cls):
        return cls.builder(cls.markup).as_markup()


class ReplyKeyboard(Keyboard):
    builder = ReplyKeyboardBuilder


class InlineKeyboard(Keyboard):
    builder = InlineKeyboardBuilder