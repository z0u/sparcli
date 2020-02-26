import numpy as np
import pytest

import sparcli.data


@pytest.mark.parametrize(
    "values,expected", [([], []), ([0], [0]), ([-1, 0, 1], [0, 0.5, 1]),]
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
        sparcli.data.CompactingSeries(max_size)
    assert "multiple of 2" in str(error.value).lower()


@pytest.mark.parametrize(
    "values,expected,scale", [([1], [1], 1), ([1, 2, 3, 4], [1.5, 3.5], 2),],
)
def test_that_series_automatically_compacts(values, expected, scale):
    series = sparcli.data.CompactingSeries(4)

    for value in values:
        series.add(value)

    assert scale == series.scale
    assert np.allclose(expected, series.values)


def test_that_weighted_head_value_is_included_in_values():
    series = sparcli.data.CompactingSeries(4)
    for value in [1, 2, 3, 4, 5]:
        series.add(value)

    values = series.values

    assert series.scale == 2
    assert series.head.size == 1
    assert series.head.mean == 5
    expected = [1.5, 3.5] + [sum([3.5, 3.5, 5]) / 3]
    assert np.allclose(expected, values)


@pytest.mark.parametrize(
    "values,expected", [([1, 2, 3], 2.0), (range(1, 1000000), 500000),],
)
def test_that_mean_calculation_is_reasonably_stable(values, expected):
    values = (float(x) for x in values)
    bucket = sparcli.data.StableBucket()

    for value in values:
        bucket.add(value)

    assert expected == bucket.mean
