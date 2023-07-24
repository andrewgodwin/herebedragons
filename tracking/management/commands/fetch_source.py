from django.core.management.base import BaseCommand

from tracking.models import Source


class Command(BaseCommand):
    help = "Fetches a single source"

    def add_arguments(self, parser):
        parser.add_argument(
            "id",
            type=int,
            help="The source ID",
        )

    def handle(self, id: int, *args, **options):
        # Get the source
        source = Source.objects.get(id=id)
        print("Fetching %s" % source)
        source.fetch()
