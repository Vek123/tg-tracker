from aiogram import Router

from apps.core.views import View
from utils.import_ import import_attr


def get_router(router_path: str):
    router = import_attr(router_path, "router")
    if not router:
        raise RuntimeError(f"Router not found in {router_path}")

    return router


def include_view(router: Router, view: View) -> None:
    observer = router.observers[view.observer.name]
    wrapper = observer(*view.observer.filters, flags=view.observer.flags, **view.observer.kwargs)
    wrapper(view.handle)
