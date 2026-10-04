from django.apps import AppConfig
from django.db.models.signals import post_migrate


def seed_on_migrate(sender, **kwargs):
    """Populate zones and monsters right after migrations if the DB is empty."""
    from .views import ensure_seed
    ensure_seed()


class DungeonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dungeon"

    def ready(self):
        post_migrate.connect(seed_on_migrate, sender=self)
