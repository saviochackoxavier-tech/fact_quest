from .views import get_player


def player_hud(request):
    return {"hud": get_player(request)}
