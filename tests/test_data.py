import numpy as np
import pytest

import sparcli.data

NAN = float("nan")
INF = float("inf")


@pytest.mark.parametrize(
    "values,expected",
    [
        ([], []),
        ([0], [0]),
        ([500, 220.1], [1, 0]),
        ([-1, 0, 1], [0, 0.5, 1]),
        ([NAN], [NAN]),
        ([INF], [NAN]),
        ([-INF], [NAN]),
        ([0, NAN, 1, INF, 2, -INF], [0, NAN, 0.5, NAN, 1, NAN]),
    ],
)
def test_that_data_can_be_normalized(values, expected, allclose):
    values = np.array(values)
    expected = np.array(expected)

    output = sparcli.data.normalize(values)

    assert allclose(expected, output)


@pytest.mark.parametrize(
    "values,expected",
    [([], []), ([1, 2, 3, 4], [1.5, 3.5]), ([NAN, 2, INF, 4, 6, -INF], [2, 4, 6])],
)
def test_that_series_can_be_compacted(values, expected, allclose):
    values = np.array(values)
    output = sparcli.data.compact(values)
    assert allclose(expected, output)


@pytest.mark.parametrize("max_size", [0, 1, 3])
def test_that_compacting_series_checks_for_max_size_constraints(max_size):
    with pytest.raises(ValueError) as error:
        sparcli.data.CompactingSeries(max_size)
    assert "multiple of 2" in str(error.value).lower()


@pytest.mark.parametrize(
    "values,expected,scale", [([1], [1], 1), ([1, 2, 3, 4], [1.5, 3.5], 2),],
)
def test_that_series_automatically_compacts(values, expected, scale, allclose):
    series = sparcli.data.CompactingSeries(4)

    for value in values:
        series.add(value)

    assert scale == series.scale
    assert allclose(expected, series.values)


@pytest.mark.parametrize(
    "in_values,out_values", [([1, 2, 3, 4], [2, 3, 4])],
)
def test_that_series_automatically_truncates(in_values, out_values, allclose):
    series = sparcli.data.CompactingSeries(4, 1)

    for value in in_values:
        series.add(value)

    assert allclose(out_values, series.values)


@pytest.mark.parametrize(
    "in_values,expected_tail,out_values",
    [([], [], []), ([1], [1], [1]), ([1, 2, 3], [1.5], [2]), ([1, NAN, 4], [1], [2])],
)
def test_that_weighted_head_value_is_included_in_values(
    in_values, expected_tail, out_values, allclose
):
    series = sparcli.data.CompactingSeries(2)
    for value in in_values:
        series.add(value)

    values = series.values

    assert allclose(expected_tail, series.tail)
    assert allclose(out_values, values)


@pytest.mark.parametrize(
    "values,expected",
    [([1, 2, 3], 2.0), (range(1, 1000000), 500000), ([1, NAN, 3], 2), ([INF, 3], 3)],
)
def test_that_mean_calculation_is_reasonably_stable(values, expected):
    values = (float(x) for x in values)
    bucket = sparcli.data.StableBucket()

    for value in values:
        bucket.add(value)

    assert expected == bucket.mean
