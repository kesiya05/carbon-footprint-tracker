import pytest

from app.factors import FACTORS, co2e


def test_co2e_multiplies_quantity_by_factor():
    assert co2e("electricity", 100) == 23.0
    assert co2e("beef", 2) == 54.0


def test_unknown_category_raises():
    with pytest.raises(KeyError):
        co2e("unicorn", 1)


def test_every_factor_has_unit_and_label():
    for key, f in FACTORS.items():
        assert f["unit"] and f["label"] and f["kg_per_unit"] > 0, key
