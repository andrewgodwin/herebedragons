from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point

from tracking.models import Location


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
    public = models.BooleanField(default=False)

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
        # Go through the list in pairs and find the two with the lowest distance
        lowest = None
        for first, second in zip(route_points, route_points[1:]):
            total_distance = first.distance.m + second.distance.m
            if lowest is None or total_distance < lowest[2]:
                lowest = (first, second, total_distance)
        # Work out the ratio between them and return that
        first, second, _ = lowest  # type: ignore
        ratio = first.distance.m / (first.distance.m + second.distance.m)
        return route_points, first.order + ratio

    def valid_locations(self) -> models.QuerySet[Location]:
        """
        Returns entity locations that we think are valid in the route
        (i.e. date bounded)
        """
        queryset = self.entity.locations
        if self.starts:
            queryset = queryset.filter(when__gte=self.starts)
        if self.ends:
            queryset = queryset.filter(when__lte=self.ends)
        return queryset


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
