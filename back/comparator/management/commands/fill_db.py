import json

from django.core.management import BaseCommand

from comparator.models import ImageCheck


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('comparator/management/commands/images.json', 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        for element in data:
            ImageCheck.objects.create(**{
                "img": element['fname'],
                "sha1": element['sha1'],
                "ssdeep": element['ssdeep'],
                "averagehash": element['averagehash'],
                "phash": element['phash'],
                "dhash": element['dhash'],
            })