import numpy as np
import pytest

import sparcli.data


@pytest.mark.parametrize(
    "values,expected", [([], []), ([0], [0]), ([1, 2, 3], [0, 0.5, 1]),]
)
def test_that_data_can_be_normalized(values, expected):
    values = np.array(values)
    output = sparcli.data.normalize(values)
    assert np.allclose(expected, output)


@pytest.mark.parametrize(
    "values,expected", [([], []), ([1, 2, 3, 4], [1.5, 3.5]),],
)
def test_that_series_can_be_compacted(values, expected):
    values = np.array(values)
    output = sparcli.data.compact(values)
    assert np.allclose(expected, output)


@pytest.mark.parametrize("values", [[1], [0, 1, 2],])
def test_that_odd_series_cant_be_compacted(values):
    values = np.array(values)

    with pytest.raises(ValueError) as error:
        sparcli.data.compact(values)

    assert "can't compact" in str(error.value).lower()
