import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Импорт данных из CSV файлов в базу данных.

    Этот класс отвечает за загрузку данных из CSV файлов,
    которые находятся в директории `data/`.
    """

    help = "Импорт данных из csv файлов."

    def handle(self, *args, **kwargs):
        """Метод обрабатывает команду импорта csv данных в БД."""

        root_directory = os.path.dirname(os.path.dirname(settings.BASE_DIR))

        filepath = os.path.join(root_directory, 'data/ingredients.csv')

        if not os.path.exists(filepath):
            return 'Файл ingredients.csv не существует.'

        with open(filepath, mode="r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            objects = []
            id_num = Ingredient.objects.all().count() + 1
            for data in reader:
                object_instance = Ingredient(
                    id=id_num,
                    name=data[0],
                    measurement_unit=data[1]
                )
                id_num += 1
                objects.append(object_instance)

            Ingredient.objects.bulk_create(objects)
        return "Данные из csv файлов успешно загружены."
