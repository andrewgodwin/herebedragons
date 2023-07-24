from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point


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

    starts = models.DateTimeField(blank=True, null=True)
    ends = models.DateTimeField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Route #{self.id} ({self.name})"

    def place_point(self, point: Point) -> tuple[list["RoutePoint"], float]:
        """
        Returns the point's progression along the path as a float, interpolated
        between the Order values of points.
        """
        # For each point, work out how far away it is
        route_points = list(
            self.points.annotate(distance=Distance("location", point)).order_by("order")
        )
        if len(route_points) < 2:
            return route_points, 0
        # Order the list by distance to find the two closest ones
        sorted_points = sorted(route_points, key=lambda p: p.distance.m)
        # Work out the ratio between them and return that
        ratio = sorted_points[0].distance.m / (
            sorted_points[0].distance.m + sorted_points[1].distance.m
        )
        return route_points, min(sorted_points[0].order, sorted_points[1].order) + ratio


class RoutePoint(models.Model):
    """
    A point along a route, with an expected time.
    """

    route = models.ForeignKey(
        "tracking.Route",
        on_delete=models.CASCADE,
        related_name="points",
    )

    order = models.IntegerField()
    name = models.CharField()
    location = models.PointField()
    radius = models.IntegerField(default=100)  # In metres
    eta = models.DateTimeField(blank=True, null=True)
    etd = models.DateTimeField(blank=True, null=True)
