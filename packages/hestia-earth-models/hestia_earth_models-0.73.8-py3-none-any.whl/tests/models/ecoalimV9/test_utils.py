from hestia_earth.models.ecoalimV9.utils import _values_from_column


def test_values_from_column():
    column = 'landTransformation+landCover[pond]+previousLandCover[permanentCropland]+country[GADM-BRA]'
    assert _values_from_column(column, '10') == {
        'landTransformation': {
            'value': 10,
            'landCover': 'pond',
            'previousLandCover': 'permanentCropland',
            'country': 'GADM-BRA'
        }
    }
