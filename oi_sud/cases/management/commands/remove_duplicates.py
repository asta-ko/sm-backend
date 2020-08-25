from django.core.management.base import BaseCommand


# from oi_sud.cases.models import Case


class Command(BaseCommand):

    def handle(self, *args, **options):
        pass
        # cases = Case.objects.filter(duplicate=False)
