"""Кастомная команда для загрузки ингредиентов из JSON-файла в базу данных."""

import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Загружает ингредиенты из data/ingredients.json в базу данных."""

    help = "Загружает ингредиенты из data/ingredients.json в базу данных"

    def handle(self, *args, **options):
        """Загружает ингредиенты из JSON-файла в базу данных."""
        json_path = settings.BASE_DIR.parent / "data" / "ingredients.json"
        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f"Файл {json_path} не найден"))
            return

        with open(json_path, "r", encoding="utf-8") as f:
            ingredients_data = json.load(f)

        existing = {ing.name: ing for ing in Ingredient.objects.all()}
        new_ingredients = []
        update_ingredients = []

        for item in ingredients_data:
            name = item.get("name")
            unit = item.get("measurement_unit")
            if not name or not unit:
                continue

            if name in existing:
                if existing[name].measurement_unit != unit:
                    existing[name].measurement_unit = unit
                    update_ingredients.append(existing[name])
            else:
                new_ingredients.append(Ingredient(
                    name=name,
                    measurement_unit=unit
                ))

        created_count = 0
        if new_ingredients:
            Ingredient.objects.bulk_create(new_ingredients)
            created_count = len(new_ingredients)

        updated_count = 0
        if update_ingredients:
            Ingredient.objects.bulk_update(
                update_ingredients,
                ['measurement_unit']
            )
            updated_count = len(update_ingredients)

        self.stdout.write(
            self.style.SUCCESS(
                f"Загрузка завершена: создано {created_count} ингредиентов, "
                f"обновлено {updated_count}"
            )
        )
