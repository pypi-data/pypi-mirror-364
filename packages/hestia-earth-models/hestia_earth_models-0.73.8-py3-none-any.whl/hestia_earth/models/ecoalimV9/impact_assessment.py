from functools import reduce
from statistics import mean
from hestia_earth.schema import IndicatorMethodTier, TermTermType
from hestia_earth.utils.tools import flatten, list_sum

from hestia_earth.models.log import logShouldRun, logRequirements
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.background_emissions import get_background_inputs, log_missing_emissions
from hestia_earth.models.utils.blank_node import group_by_keys
from .utils import get_input_mappings, process_input, parse_term_id
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "cycle": {
            "@type": "Cycle",
            "inputs": [{
                "@type": "Input",
                "value": "> 0",
                "none": {
                    "fromCycle": "True",
                    "producedInCycle": "True"
                }
            }],
            "optional": {
                "animals": [{
                    "@type": "Animal",
                    "inputs": [{
                        "@type": "Input",
                        "value": "> 0",
                        "none": {
                            "fromCycle": "True",
                            "producedInCycle": "True"
                        }
                    }]
                }]
            }
        }
    }
}
RETURNS = {
    "Indicator": [{
        "term": "",
        "value": "",
        "methodTier": "background",
        "inputs": "",
        "operation": ""
    }]
}
LOOKUPS = {
    "ecoalim-resourceUse": "resourceUse-",
    "animalProduct": "ecoalimMapping",
    "crop": "ecoalimMapping",
    "feedFoodAdditive": "ecoalimMapping",
    "forage": "ecoalimMapping",
    "processedFood": "ecoalimMapping"
}
MODEL_KEY = 'impact_assessment'
TIER = IndicatorMethodTier.BACKGROUND.value


def _indicator(
    term_id: str,
    value: float,
    input: dict,
    country_id: str = None,
    key_id: str = None,
    land_cover_id: str = None,
    previous_land_cover_id: str = None,
):
    indicator = _new_indicator(term_id, MODEL, land_cover_id, previous_land_cover_id, country_id, key_id)
    indicator['value'] = value
    indicator['methodTier'] = TIER
    indicator['inputs'] = [input.get('term')]
    if input.get('operation'):
        indicator['operation'] = input.get('operation')
    return indicator


def _run_input(impact_assessment: dict):
    log_missing_emissions_func = log_missing_emissions(
        impact_assessment, TermTermType.RESOURCEUSE, model=MODEL, methodTier=TIER
    )

    def run(inputs: list):
        input = inputs[0]
        input_term_id = input.get('term', {}).get('@id')
        input_value = list_sum(flatten(input.get('value', []) for input in inputs))
        mappings = get_input_mappings(MODEL, input)
        has_mappings = len(mappings) > 0

        logRequirements(impact_assessment, model=MODEL, term=input_term_id, model_key=MODEL_KEY,
                        has_mappings=has_mappings,
                        mappings=';'.join([v[1] for v in mappings]),
                        input_value=input_value)

        should_run = all([has_mappings, input_value])
        logShouldRun(
            impact_assessment, MODEL, input_term_id, should_run, methodTier=TIER, model_key=MODEL_KEY
        )

        results = process_input(
            impact_assessment, input, mappings, TermTermType.RESOURCEUSE, model_key=MODEL_KEY
        ) if should_run else {}
        log_missing_emissions_func(input_term_id, list(map(parse_term_id, results.keys())))
        return [
            _indicator(
                term_id=parse_term_id(term_id),
                value=mean([v['value'] * v['coefficient'] for v in values]) * input_value,
                input=input,
                country_id=values[0].get('country'),
                key_id=values[0].get('key'),
                land_cover_id=values[0].get('landCover'),
                previous_land_cover_id=values[0].get('previousLandCover'),
            )
            for term_id, values in results.items()
        ]
    return run


def run(impact_assessment: dict):
    inputs = get_background_inputs(impact_assessment.get('cycle', {}))
    grouped_inputs = reduce(group_by_keys(['term', 'operation']), inputs, {})
    return flatten(map(_run_input(impact_assessment), grouped_inputs.values()))
