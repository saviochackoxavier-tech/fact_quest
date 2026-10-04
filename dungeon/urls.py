from django.urls import path
from . import views

urlpatterns = [
    path("", views.world_map, name="map"),
    path("battle/<int:monster_id>/", views.battle, name="battle"),
    path("battle/<int:monster_id>/action/", views.battle_action, name="battle_action"),
    path("custom/", views.custom_arena, name="custom"),
    path("custom/scan/", views.custom_scan, name="custom_scan"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("rename/", views.rename, name="rename"),
]
