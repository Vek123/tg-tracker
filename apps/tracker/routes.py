from aiogram import Router

from apps.core.routes import include_view
from apps.tracker import views


router = Router()
include_view(router, views.AddTrackerCredentialsCommandView())
include_view(router, views.StartCommandView())
include_view(router, views.DeleteSecretTrackerFilterView())
include_view(router, views.UpdateSecretTrackerFilterView())
include_view(router, views.ProcessTrackerOrgIdStateView())
include_view(router, views.ProcessTrackerTokenStateView())


router.message()
