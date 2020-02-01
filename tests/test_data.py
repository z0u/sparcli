import numpy as np
import pytest

import sparcli.data


@pytest.mark.parametrize("values,expected", [
    ([], []),
    ([0], [0]),
    ([0.1], [0]),
    ([1, 2, 3], [0, 0.5, 1]),
])
def test_that_data_can_be_normalized(values, expected):
    series = np.array(values)
    output = sparcli.data.normalize(series)
    assert np.allclose(expected, output)
