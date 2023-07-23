from django.conf import settings
from django.db import models

from tracking.models.location import Location


class Entity(models.Model):
    """
    Something that can be tracked.
    """

    name = models.CharField(max_length=200)

    owners = models.ManyToManyField(settings.AUTH_USER_MODEL)

    public = models.BooleanField(default=False)
    public_inaccuracy = models.IntegerField(default=1000)  # In metres

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "entities"

    def __str__(self):
        return f"Entity #{self.id} ({self.name})"

    def most_recent_location(self) -> Location | None:
        try:
            return self.locations.order_by("-when")[0]
        except IndexError:
            return None
