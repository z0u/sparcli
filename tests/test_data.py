import pytest

import sparcli.data


@pytest.mark.parametrize("values,expected", [
    ([], []),
    ([0], [0.5]),
    ([0.1], [0.5]),
    ([1, 2, 3], [0, 0.5, 1]),
    ([1, None, 3], [0, None, 1]),
])
def test_that_data_can_be_normalized(values, expected):
    output = sparcli.data.normalize(values)
    assert expected == output
