"""Emission factors in kg CO2e per unit.

IMPORTANT: these are rounded approximations used to make the app work out of the box.
Replace them with the official numbers for your country and year (for example UK DEFRA
conversion factors or US EPA emission factors) before quoting any result.
"""

FACTORS = {
    "electricity": {"unit": "kWh", "kg_per_unit": 0.23, "label": "Electricity"},
    "natural_gas": {"unit": "m3", "kg_per_unit": 2.0, "label": "Natural gas"},
    "diesel": {"unit": "litre", "kg_per_unit": 2.7, "label": "Diesel (vehicles)"},
    "petrol": {"unit": "litre", "kg_per_unit": 2.3, "label": "Petrol (vehicles)"},
    "food_waste": {"unit": "kg", "kg_per_unit": 0.6, "label": "Food waste"},
    "beef": {"unit": "kg", "kg_per_unit": 27.0, "label": "Beef purchased"},
    "poultry": {"unit": "kg", "kg_per_unit": 6.9, "label": "Poultry purchased"},
    "dairy": {"unit": "kg", "kg_per_unit": 3.2, "label": "Dairy purchased"},
    "vegetables": {"unit": "kg", "kg_per_unit": 2.0, "label": "Vegetables purchased"},
    "water": {"unit": "m3", "kg_per_unit": 0.34, "label": "Water"},
}


def co2e(category: str, quantity: float) -> float:
    if category not in FACTORS:
        raise KeyError(category)
    return round(quantity * FACTORS[category]["kg_per_unit"], 3)
