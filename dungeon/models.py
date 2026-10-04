from django.db import models


class DungeonZone(models.Model):
    name = models.CharField(max_length=80)
    description = models.TextField()
    danger_level = models.PositiveSmallIntegerField(default=1)
    badge_icon = models.CharField(max_length=8, default="🏰")

    def __str__(self):
        return self.name


class RumorMonster(models.Model):
    TYPES = [("Goblin", "Goblin"), ("Dragon", "Dragon"), ("Phantom", "Phantom")]
    zone = models.ForeignKey(DungeonZone, on_delete=models.CASCADE, related_name="monsters")
    name = models.CharField(max_length=80)
    claim_text = models.TextField()
    monster_type = models.CharField(max_length=10, choices=TYPES, default="Goblin")
    difficulty = models.PositiveSmallIntegerField(default=1)

    @property
    def icon(self):
        return {"Goblin": "👺", "Dragon": "🐉", "Phantom": "👻"}.get(self.monster_type, "👾")

    def __str__(self):
        return f"{self.name} ({self.monster_type})"


class PlayerSession(models.Model):
    player_name = models.CharField(max_length=40, default="Rookie")
    hp = models.IntegerField(default=100)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    dungeons_cleared = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.player_name} L{self.level}"


class LeaderboardEntry(models.Model):
    player_name = models.CharField(max_length=40)
    score = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-score", "timestamp"]

    def __str__(self):
        return f"{self.player_name}: {self.score}"
