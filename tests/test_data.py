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


@pytest.mark.parametrize("max_size", [0, 1, 3])
def test_that_compacting_series_checks_for_max_size_constraints(max_size):
    with pytest.raises(ValueError) as error:
        sparcli.data.CompactingSeries([], max_size)
    assert "multiple of 2" in str(error.value).lower()


@pytest.mark.parametrize(
    "values,expected", [([], [4]), ([1, 2, 3], [1.5, 3.5]),],
)
def test_that_series_automatically_compacts_when_it_reaches_capacity(values, expected):
    series = sparcli.data.CompactingSeries(values, 4)
    series.append(4)
    assert np.allclose(expected, series.values)
