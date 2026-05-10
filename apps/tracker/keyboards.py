from aiogram.types.inline_keyboard_button import InlineKeyboardButton

from apps.ai.dialog import ApproveRequest
from apps.core.keyboards import InlineKeyboard


class TrackerCredentialsExistedSecretKeyboard(InlineKeyboard):
    UPDATE_DATA = "login_existed_secret_update_data"
    DELETE_DATA = "login_existed_secret_delete_data"
    markup = [
        [InlineKeyboardButton(text="Обновить", callback_data=UPDATE_DATA), InlineKeyboardButton(text="Удалить", callback_data=DELETE_DATA)],
    ]


class ConfirmMcpRequestKeyboard(InlineKeyboard):
    CONFIRM = "confirm_mcp_request"
    SELECT_BUTTON_PREFIX = "confirm_select_"
    markup = [
        [InlineKeyboardButton(text="Подтвердить", callback_data=CONFIRM)],
    ]

    @classmethod
    def build(cls, requests: list[ApproveRequest]) -> InlineKeyboard.builder:
        buttons = [[InlineKeyboardButton(
            text=request.title,
            style="success" if request.approve else "danger",
            callback_data=cls.SELECT_BUTTON_PREFIX + request.id,
        )] for request in requests]
        markup = buttons + cls.markup
        return cls.builder(markup).as_markup()
