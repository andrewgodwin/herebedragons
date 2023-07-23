from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

SRID_LATLONG = 4326
SRID_SPHMERC = 3857


class Location(models.Model):
    """
    The location of an Entity at a certain point in time.
    """

    entity = models.ForeignKey(
        "tracking.Entity",
        on_delete=models.CASCADE,
        related_name="locations",
    )
    source = models.ForeignKey(
        "tracking.Source",
        on_delete=models.PROTECT,
        related_name="locations",
    )
    when = models.DateTimeField()
    where = models.PointField()

    accuracy = models.FloatField(blank=True, null=True)  # In metres
    speed = models.FloatField(blank=True, null=True)  # In metres/sec
    extra = models.JSONField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Location #{self.id} ({self.when})"

    def inaccurate_long_lat(self) -> tuple[float, float]:
        """
        Returns a predictably inaccurate lat/long based on the entity's settings
        """
        # First, convert to spherical mercator
        sm_point = self.where.transform(SRID_SPHMERC, clone=True)
        # Round it according to the accuracy setting
        accuracy = self.entity.public_inaccuracy
        inacc_point = Point(
            (int(sm_point.x / accuracy) + 0.5) * accuracy,
            (int(sm_point.y / accuracy) + 0.5) * accuracy,
            srid=SRID_SPHMERC,
        )
        # Return lat/long values
        inacc_point.transform(SRID_LATLONG)
        return inacc_point.x, inacc_point.y
