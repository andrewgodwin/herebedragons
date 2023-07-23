from django.contrib.gis.db import models


class Route(models.Model):
    """
    A path an Entity is expected to follow, and can be shown abstractly.
    """

    entity = models.ForeignKey(
        "tracking.Entity",
        on_delete=models.CASCADE,
        related_name="routes",
    )

    name = models.CharField(max_length=200)
    description = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Route #{self.id} ({self.name})"


class RoutePoint(models.Model):
    """
    A point along a route, with an expected time.
    """

    route = models.ForeignKey(
        "tracking.Route",
        on_delete=models.CASCADE,
        related_name="points",
    )

    location = models.PointField()
    radius = models.IntegerField(default=100)  # In metres
    eta = models.DateTimeField(blank=True, null=True)
    etd = models.DateTimeField(blank=True, null=True)
