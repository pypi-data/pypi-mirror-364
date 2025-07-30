import pandas as pd
import pytest

from bonini2025 import pth_clean


@pytest.fixture()
def meas():
    return pd.read_csv(pth_clean / "fig4.csv", sep=";", comment="#", index_col=["hour"])


def test_fig3_values_are_defined(meas):
    for variety in ("cs", "mc"):
        for trt in ("OF", "AV"):
            assert len(meas[f"tr_{variety}_{trt}"]) > 0
