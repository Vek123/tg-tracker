from aiogram.fsm.state import State, StatesGroup


class TrackerCreds(StatesGroup):
    token = State()
    org_id = State()
