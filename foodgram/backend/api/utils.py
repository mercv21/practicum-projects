"""Утилиты для формирования списка покупок."""

from recipes.models import ShoppingCart


def generate_shopping_list_text(user):
    """Формирует текстовый список покупок для пользователя."""
    cart_items = ShoppingCart.objects.filter(
        user=user
    ).select_related('recipe').prefetch_related(
        'recipe__ingredients_list__ingredient'
    )

    ingredients_dict = {}
    for cart_item in cart_items:
        for item in cart_item.recipe.ingredients_list.all():
            ingredient = item.ingredient
            name = ingredient.name
            unit = ingredient.measurement_unit
            amount = item.amount
            key = f"{name}|{unit}"
            if key in ingredients_dict:
                ingredients_dict[key]['amount'] += amount
            else:
                ingredients_dict[key] = {
                    'name': name,
                    'unit': unit,
                    'amount': amount,
                }

    lines = [
        f"{data['name']} ({data['unit']}) — {data['amount']}"
        for data in sorted(
            ingredients_dict.values(), key=lambda x: x['name']
        )
    ]
    return "\n".join(lines)
