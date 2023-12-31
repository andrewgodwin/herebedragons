from django.contrib.gis import admin
from django.contrib.gis.admin.options import GeoModelAdminMixin

from tracking.models import Entity, Location, Route, RoutePoint, Source


@admin.register(Location)
class LocationAdmin(admin.GISModelAdmin):
    list_display = ["id", "when", "source"]
    gis_widget_kwargs = {
        "attrs": {
            "default_lat": 40,
            "default_lon": -105,
            "default_zoom": 6,
        }
    }


@admin.register(Entity)
class EntityAdmin(admin.GISModelAdmin):
    list_display = ["id", "name", "public", "created"]
    list_display_links = ["id", "name"]


@admin.register(Source)
class SourceAdmin(admin.GISModelAdmin):
    list_display = ["id", "entity", "type", "created"]


class RoutePointInline(GeoModelAdminMixin, admin.StackedInline):
    model = RoutePoint
    ordering = ["order"]
    gis_widget_kwargs = {
        "attrs": {
            "default_lat": 40,
            "default_lon": -105,
            "default_zoom": 6,
        }
    }


@admin.register(Route)
class RouteAdmin(admin.GISModelAdmin):
    list_display = ["id", "name", "public", "created"]
    list_display_links = ["id", "name"]
    inlines = [RoutePointInline]
