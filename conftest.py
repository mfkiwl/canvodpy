"""Pytest configuration for canvodpy workspace."""

from pathlib import Path
import pytest


# Test data location (submodule)
TEST_DATA_ROOT = Path(__file__).parent / "test-data"

# Example data location (submodule)
EXAMPLES_ROOT = Path(__file__).parent / "examples"


# ============================================================================
# Test Data Fixtures (for validation testing with falsified data)
# ============================================================================

@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """
    Root directory for test data.
    
    Returns test-data submodule path. Verifies it exists and is initialized.
    This contains falsified/corrupted files for testing error handling.
    """
    if not TEST_DATA_ROOT.exists():
        pytest.skip(
            "Test data submodule not initialized. Run: "
            "git submodule update --init test-data"
        )
    return TEST_DATA_ROOT


@pytest.fixture(scope="session")
def valid_rinex_dir(test_data_dir: Path) -> Path:
    """Directory containing valid RINEX test files."""
    return test_data_dir / "valid" / "rinex"


@pytest.fixture(scope="session")
def valid_aux_dir(test_data_dir: Path) -> Path:
    """Directory containing valid auxiliary test files."""
    return test_data_dir / "valid" / "aux"


@pytest.fixture(scope="session")
def corrupted_rinex_dir(test_data_dir: Path) -> Path:
    """Directory containing corrupted RINEX files for error testing."""
    return test_data_dir / "corrupted" / "rinex"


@pytest.fixture(scope="session")
def corrupted_aux_dir(test_data_dir: Path) -> Path:
    """Directory containing corrupted auxiliary files for error testing."""
    return test_data_dir / "corrupted" / "aux"


@pytest.fixture(scope="session")
def edge_case_dir(test_data_dir: Path) -> Path:
    """Directory containing edge case test files."""
    return test_data_dir / "edge_cases"


@pytest.fixture
def sample_rinex_file(valid_rinex_dir: Path) -> Path:
    """Path to a standard valid RINEX file."""
    sample = valid_rinex_dir / "2023_001_canopy.rnx"
    if not sample.exists():
        pytest.skip(f"Sample RINEX file not found: {sample}")
    return sample


@pytest.fixture
def sample_sp3_file(valid_aux_dir: Path) -> Path:
    """Path to a standard valid SP3 file."""
    sample = valid_aux_dir / "COD0MGXFIN_20230010000_01D_05M_ORB.SP3"
    if not sample.exists():
        pytest.skip(f"Sample SP3 file not found: {sample}")
    return sample


@pytest.fixture
def sample_clk_file(valid_aux_dir: Path) -> Path:
    """Path to a standard valid CLK file."""
    sample = valid_aux_dir / "COD0MGXFIN_20230010000_01D_30S_CLK.CLK"
    if not sample.exists():
        pytest.skip(f"Sample CLK file not found: {sample}")
    return sample


# Mark for tests that require test data
requires_test_data = pytest.mark.skipif(
    not TEST_DATA_ROOT.exists(),
    reason="Test data submodule not initialized"
)


# ============================================================================
# Example Data Fixtures (for demos/documentation with real data)
# ============================================================================

@pytest.fixture(scope="session")
def examples_dir() -> Path:
    """
    Root directory for example data.
    
    Returns examples submodule path. Verifies it exists and is initialized.
    This contains clean real-world data for demos and documentation.
    """
    if not EXAMPLES_ROOT.exists():
        pytest.skip(
            "Examples submodule not initialized. Run: "
            "git submodule update --init examples"
        )
    return EXAMPLES_ROOT


@pytest.fixture(scope="session")
def rosalia_rinex_dir(examples_dir: Path) -> Path:
    """Directory containing Rosalia site RINEX files."""
    return examples_dir / "rosalia/2023/001/rinex"


@pytest.fixture(scope="session")
def rosalia_aux_dir(examples_dir: Path) -> Path:
    """Directory containing Rosalia site auxiliary files."""
    return examples_dir / "rosalia/2023/001/aux"


@pytest.fixture
def rosalia_canopy_rinex(rosalia_rinex_dir: Path) -> Path:
    """Path to Rosalia canopy RINEX file."""
    sample = rosalia_rinex_dir / "canopy_20230010000.rnx"
    if not sample.exists():
        pytest.skip(f"Rosalia canopy RINEX not found: {sample}")
    return sample


@pytest.fixture
def rosalia_reference_rinex(rosalia_rinex_dir: Path) -> Path:
    """Path to Rosalia reference RINEX file."""
    sample = rosalia_rinex_dir / "reference_20230010000.rnx"
    if not sample.exists():
        pytest.skip(f"Rosalia reference RINEX not found: {sample}")
    return sample


# Mark for tests that require example data
requires_examples = pytest.mark.skipif(
    not EXAMPLES_ROOT.exists(),
    reason="Examples submodule not initialized"
)
