"""Django urlpatterns declaration for nautobatfishbot plugin."""
from django.urls import path, include
from django.contrib import admin
from . import views

urlpatterns = [
    # find URL with the python: reverse("plugins:nautobatfishbot:nautobatfishbot_homepage")
    #   resolve("/plugins/nautobatfishbot/nautobatfishbot_homepage/")
    #   can also be useful
    path('nautobatfishbot/', views.nautobatfishbot, name="nautobatfishbot_homepage")]

    # rest framework would look like
    # reverse("plugins-api:nautobatfishbot-api:nautobatfishbot-list")

    # restframework detailed view
    # reverse("plugins-api:nautobatfishbot-api:nautobatfishbot-detail", kwargs={"pk":obj.pk})

    # /api/plugins/nautobatfishbot/nautbatfishbot/
    # /api/plugins/nautobatfishbot/nautbatfishbot/<uuid>/


# urlpatterns = [
#     path('nautobatfishbot/', views.nautobatfishbot.as_view(), name="nautobatfishbot_homepage")]