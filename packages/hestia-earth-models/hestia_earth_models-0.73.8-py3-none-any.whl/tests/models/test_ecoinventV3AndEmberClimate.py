import json
from unittest.mock import patch

from tests.utils import fixtures_path, fake_new_emission
from hestia_earth.models.ecoinventV3AndEmberClimate import MODEL, run

class_path = f"hestia_earth.models.{MODEL}"
fixtures_folder = f"{fixtures_path}/{MODEL}"

ELECTRICITY_TERMS = [
    'electricityGridMarketMix',
    'electricityGridRenewableMix'
]


@patch(f"{class_path}.get_electricity_grid_mix_terms", return_value=ELECTRICITY_TERMS)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run('all', cycle)
    assert result == expected
