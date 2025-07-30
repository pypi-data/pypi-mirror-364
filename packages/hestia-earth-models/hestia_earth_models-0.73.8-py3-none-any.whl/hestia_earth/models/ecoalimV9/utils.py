from functools import lru_cache, reduce
from hestia_earth.schema import EmissionMethodTier, TermTermType
from hestia_earth.utils.lookup import download_lookup, _is_missing_value, column_name, lookup_columns
from hestia_earth.utils.tools import non_empty_list, safe_parse_float

from hestia_earth.models.log import debugValues, logShouldRun
from hestia_earth.models.utils import _omit
from hestia_earth.models.utils.term import get_lookup_value
from . import MODEL

_LOOKUP_INDEX_KEY = column_name('ecoalimMappingName')
_TIER = EmissionMethodTier.BACKGROUND.value


def get_input_mappings(model: str, input: dict):
    term = input.get('term', {})
    term_id = term.get('@id')
    value = get_lookup_value(term, 'ecoalimMapping', model=model, term=term_id)
    mappings = non_empty_list(value.split(';')) if value else []
    return [(m.split(':')[0], m.split(':')[1]) for m in mappings]


def parse_term_id(term_id: str): return term_id.split('-')[0]


def _process_mapping(node: dict, input: dict, term_type: TermTermType, **log_args):
    input_term_id = input.get('term', {}).get('@id')
    operation_term_id = input.get('operation', {}).get('@id')
    animal_term_id = input.get('animal', {}).get('@id')

    def add(prev: dict, mapping: tuple):
        gadm_id, ecoalim_key = mapping
        # all countries have the same coefficient
        coefficient = 1
        values = ecoalim_values(ecoalim_key, term_type)
        for term_id, data in values:
            # log run on each node so we know it did run
            logShouldRun(node, MODEL, input_term_id, True, methodTier=_TIER, emission_id=term_id)
            debugValues(node, model=MODEL, term=term_id,
                        value=data.get('value'),
                        coefficient=coefficient,
                        input=input_term_id,
                        operation=operation_term_id,
                        animal=animal_term_id,
                        **log_args)
            group_id = '-'.join(non_empty_list([term_id] + list(_omit(data, ['value']).values())))
            prev[group_id] = prev.get(group_id, []) + [data | {'coefficient': coefficient}]
        return prev
    return add


def process_input(node: dict, input: dict, mappings: list, term_type: TermTermType, **log_args):
    return reduce(_process_mapping(node, input, term_type, **log_args), mappings, {})


_KEY_TO_FIELD = {
    'inputs': 'key'
}


def _key_to_field(key: str): return _KEY_TO_FIELD.get(key) or key


def _values_from_column(column: str, value: str):
    values = column.split('+')
    term_id = values[0]
    value = safe_parse_float(value, default=None)
    return {
        term_id: {
            'value': value
        } | {
            _key_to_field(v.split('[')[0]): v.split('[')[1][:-1] for v in values[1:]
        }
    } if all([
        column != _LOOKUP_INDEX_KEY,
        not _is_missing_value(value)
    ]) else {}


@lru_cache()
def _build_lookup(term_type: str):
    lookup = download_lookup(f"ecoalim-{term_type}.csv", keep_in_memory=False)
    columns = lookup_columns(lookup)
    return {
        row[_LOOKUP_INDEX_KEY]: reduce(
            lambda prev, curr: prev | _values_from_column(curr, row[curr]),
            columns,
            {}
        )
        for row in lookup
    }


@lru_cache()
def ecoalim_values(mapping: str, term_type: TermTermType):
    data = _build_lookup(term_type.value)
    return list(data[mapping].items())
