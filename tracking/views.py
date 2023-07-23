from django.shortcuts import get_object_or_404, render

from tracking.models import Entity


def entity_view(request, id):
    entity = get_object_or_404(Entity, id=id)
    recent_point = entity.most_recent_location()
    if recent_point is not None:
        longitude, latitude = recent_point.inaccurate_long_lat()
    else:
        longitude, latitude = None, None
    return render(
        request,
        "entity.html",
        {
            "entity": entity,
            "longitude": longitude,
            "latitude": latitude,
        },
    )
