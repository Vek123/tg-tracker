from aiogram import Router

from apps.core.routes import get_router

router = Router()
router.include_router(get_router("apps.tracker.routes"))
