from django.urls import include, path

from rest_framework.routers import SimpleRouter

from .api import AuthViewSet,CityViewSet,CountryCodeViewSet,FestivalViewSet,ContactViewSet,UserViewSet


router = SimpleRouter()

router.register(
    "auth",
    AuthViewSet,
    basename="auth"
)

router.register(
    "cities",
    CityViewSet,
    basename="cities",
)

router.register(
    "country-codes",
    CountryCodeViewSet,
    basename="country-codes",
)

router.register(
    "festivals",
    FestivalViewSet,
    basename="festivals",
)

router.register(
    "contacts",
    ContactViewSet,
    basename="contacts",
)

router.register(
    "users",
    UserViewSet,
    basename="users",
)

urlpatterns = [
    path("", include(router.urls)),
]