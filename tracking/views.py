from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from tracking.models import Entity, Route, Source


def entity_view(request, id):
    entity = get_object_or_404(Entity, id=id)
    recent_point = entity.most_recent_location()
    return render(
        request,
        "entity.html",
        {
            "entity": entity,
            "point": recent_point,
            "accuracy": entity.public_accuracy,
        },
    )


def route_view(request, id):
    route = get_object_or_404(Route, id=id)

    # Work out if we're at a point along the route
    recent_point = route.entity.most_recent_location()
    if recent_point:
        route_points, point_progression = route.place_point(recent_point.where)
    else:
        route_points = route.points.order_by("order")
        point_progression = None

    # Build the visual route representation
    point_placed = False
    distance_to_stop = None
    route_items = []
    for first, second in zip(route_points, route_points[1:]):
        # Is it at this first point?
        if first.distance.m <= first.radius:
            route_items.append(
                {"type": "route_point", "route_point": first, "here": True}
            )
            point_placed = True
        else:
            route_items.append({"type": "route_point", "route_point": first})
        # Is it in this segment?
        if (
            not point_placed
            and point_progression
            and (first.order < point_progression < second.order)
        ):
            route_items.append(
                {
                    "type": "segment",
                    "here": True,
                    "progression": point_progression - first.order,
                    "percent": "%s%%" % int((point_progression - first.order) * 100),
                }
            )
            distance_to_stop = second.distance.km
        else:
            route_items.append(
                {
                    "type": "segment",
                }
            )
    # Handle the final point
    if not point_placed and second.distance.m <= second.radius:
        route_items.append({"type": "route_point", "route_point": second, "here": True})
        point_placed = True
    else:
        route_items.append({"type": "route_point", "route_point": second})

    # Build the latlongs table for JS
    route_line = []
    for route_point in route_points:
        route_line.append([route_point.location.y, route_point.location.x])

    return render(
        request,
        "route.html",
        {
            "entity": route.entity,
            "point": recent_point,
            "route_items": route_items,
            "route_line": route_line,
            "route": route,
            "distance_to_stop": distance_to_stop,
        },
    )


def source_fetch(request, id):
    source = get_object_or_404(Source, id=id)
    source.fetch()
    return HttpResponse("Fetched.")
