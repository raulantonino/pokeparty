from django.urls import path

from . import views

app_name = "roster"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("capture/", views.capture_pokemon_view, name="capture"),
    path("optimize/", views.optimize_best_team_view, name="optimize"),
    path("release/<int:entry_id>/", views.release_pokemon_view, name="release"),
]