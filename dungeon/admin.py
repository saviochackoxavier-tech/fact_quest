from django.contrib import admin
from .models import DungeonZone, RumorMonster, PlayerSession, LeaderboardEntry
for m in (DungeonZone, RumorMonster, PlayerSession, LeaderboardEntry):
    admin.site.register(m)
