import pandas as pd
import pytest

from bonini2025 import pth_clean


@pytest.fixture()
def meas():
    return pd.read_csv(pth_clean / "fig1.csv", sep=";", comment="#", index_col=["doy"])


def test_fig1_values_are_defined(meas):
    for trt in ("OF", "AV"):
        assert len(meas[f"par_direct_{trt}"]) > 0
        assert len(meas[f"par_diff_{trt}"]) > 0
