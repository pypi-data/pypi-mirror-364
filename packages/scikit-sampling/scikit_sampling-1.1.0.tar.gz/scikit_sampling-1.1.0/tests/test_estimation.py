import pytest
from sksampling.estimation import _get_z_score, confidence_level, sample_size


def test_sample_size_basic():
    """
    Tests the sample_size function with a few known sets of inputs and
    expected outputs.
    """
    error_margin = 1
    # Test case from original print statement
    assert sample_size(100_000, 0.95, 0.02) == pytest.approx(2345, abs=error_margin)
    # Test with a smaller population
    assert sample_size(500, 0.95, 0.05) == pytest.approx(218, abs=error_margin)
    # Test with higher confidence and smaller interval
    assert sample_size(10_000, 0.99, 0.01) == pytest.approx(6239, abs=error_margin)
    # Test with a very large population, approaching the infinite case
    assert sample_size(1_000_000, 0.95, 0.05) == pytest.approx(385, abs=error_margin)


def test_z_score():
    """
    Tests the _get_z_score helper function with common confidence levels.
    """
    error_margin = 1e-2
    # Z-score for 90% confidence level should be approximately 1.645
    assert _get_z_score(0.90) == pytest.approx(1.645, abs=error_margin)
    # Z-score for 95% confidence level should be approximately 1.96
    assert _get_z_score(0.95) == pytest.approx(1.96, abs=error_margin)
    # Z-score for 99% confidence level should be approximately 2.58
    assert _get_z_score(0.99) == pytest.approx(2.58, abs=error_margin)


def test_confidence_level():
    """
    Tests the confidence_level function by checking if it's the inverse
    of the sample_size function for a few cases.
    """
    error_margin = 1e-2
    # Test case from sample_size test
    assert confidence_level(2345, 100_000, 0.02) == pytest.approx(
        0.95, abs=error_margin
    )
    # Test with a smaller population
    assert confidence_level(218, 500, 0.05) == pytest.approx(0.95, abs=error_margin)
    # Test with higher confidence and smaller interval
    assert confidence_level(6239, 10_000, 0.01) == pytest.approx(0.99, abs=error_margin)
    # Test with a very large population, approaching the infinite case
    assert confidence_level(385, 1_000_000, 0.05) == pytest.approx(
        0.95, abs=error_margin
    )


def test_confidence_level_edge_cases():
    """
    Tests edge cases for the confidence_level function.
    """
    # Test exception with sample_size >= population_size
    assert confidence_level(10_000, 1000, 0.02) == 1.0
    # Test case where z_squared would be negative due to invalid inputs
    # (e.g., negative sample_size), which should return a confidence level of 0.0.
    assert confidence_level(-1, 100, 0.02) == 0.0
