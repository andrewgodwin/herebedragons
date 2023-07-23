from django.contrib.gis.db import models


class Source(models.Model):
    """
    Something that provides location information for an entity.
    """

    entity = models.ForeignKey(
        "tracking.Entity",
        on_delete=models.CASCADE,
        related_name="sources",
    )

    type = models.CharField(max_length=100)
    config = models.JSONField()

    query_interval = models.IntegerField(blank=True, null=True)  # In seconds
    query_last = models.DateTimeField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Source #{self.id} ({self.type})"
