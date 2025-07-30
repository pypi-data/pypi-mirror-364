# {# pkglts, glabpkg_dev
import bonini2025


def test_package_exists():
    assert bonini2025.__version__

# #}
# {# pkglts, glabdata, after glabpkg_dev

def test_paths_are_valid():
    assert bonini2025.pth_clean.exists()
    try:
        assert bonini2025.pth_raw.exists()
    except AttributeError:
        pass  # package not installed in editable mode

# #}
