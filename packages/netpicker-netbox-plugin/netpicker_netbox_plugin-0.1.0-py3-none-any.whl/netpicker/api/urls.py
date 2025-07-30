from netbox.api.routers import NetBoxRouter
from . import views

router = NetBoxRouter()
app_name = 'netpicker'
urlpatterns = router.urls
