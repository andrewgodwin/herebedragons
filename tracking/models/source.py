import httpx
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from fastkml import kml

from tracking.models.location import SRID_LATLONG, Location


class Source(models.Model):
    """
    Something that provides location information for an entity.
    """

    TYPE_CHOICES = [
        ("manual", "manual"),
        ("garmin-kml", "garmin-kml"),
        ("aprs", "aprs"),
    ]

    entity = models.ForeignKey(
        "tracking.Entity",
        on_delete=models.CASCADE,
        related_name="sources",
    )

    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    config = models.JSONField()

    query_interval = models.IntegerField(blank=True, null=True)  # In seconds
    query_last = models.DateTimeField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Source #{self.id} ({self.type})"

    def fetch(self):
        if self.type == "manual":
            pass
        elif self.type == "garmin-kml":
            # Fetch the KML
            response = httpx.get(self.config["url"])
            if response.status_code != 200:
                raise ValueError(f"Got bad response from KML URL: {response}")
            k = kml.KML()
            k.from_string(response.text)
            outerFeature = list(k.features())
            innerFeature = list(outerFeature[0].features())
            placemarks = list(innerFeature[0].features())
            # Figure out the details
            placemark = placemarks[0]
            where = Point(placemark.geometry.x, placemark.geometry.y, srid=SRID_LATLONG)
            when = placemark.timeStamp
            extended_data = {
                d.name.lower(): d.value for d in placemark.extended_data.elements
            }
            speed = None
            if "velocity" in extended_data:
                speed = (
                    float(extended_data["velocity"].split()[0]) * 0.2777778
                )  # kmh to m/s
            # See if there is a point for that already
            if not self.entity.locations.filter(when=when).exists():
                location = Location.objects.create(
                    entity=self.entity, source=self, when=when, where=where, speed=speed
                )
                print(f"Saved new location {location}")
            else:
                print("Location already logged")
