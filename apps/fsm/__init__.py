import settings

from utils.import_ import import_attr


def init_fsm_storage():
    return import_attr(settings.FSM_STORAGE["path"])(**{k: v for k, v in settings.FSM_STORAGE.items() if k != "path"})
