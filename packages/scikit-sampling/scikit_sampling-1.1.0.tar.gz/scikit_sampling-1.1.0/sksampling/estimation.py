import math
import scipy.stats as st


def _get_z_score(confidence_level: float) -> float:
    """
    Retrieves the Z-score for a given confidence level.

    Args:
        confidence_level: The confidence level as a float (e.g., 0.95 for 95%).

    Returns:
        The Z-score for the given confidence level.
    """
    return st.norm.ppf(1 - (1 - confidence_level) / 2)


def sample_size(
    population_size: int,
    confidence_level: float = 0.95,
    confidence_interval: float = 0.02,
) -> int:
    """
    Calculates the sample size for a finite population using Cochran's formula.

    Args:
        population_size: The total size of the population.
        confidence_level: The desired confidence level (e.g., 0.95 for 95%).
        confidence_interval: The desired confidence interval (margin of error).
                             Default is 0.02 (2%).

    Returns:
        The calculated sample size as an integer.
    """

    # For sample size calculation, we assume the worst-case variance, where p=0.5
    p = 0.5
    z_score = _get_z_score(confidence_level)
    # Calculate sample size for an infinite population
    n_0 = (z_score**2 * p * (1 - p)) / (confidence_interval**2)
    # Adjust sample size for the finite population
    n = n_0 / (1 + (n_0 - 1) / population_size)

    return int(math.ceil(n))


def confidence_level(
    sample_size: int,
    population_size: int,
    confidence_interval: float = 0.02,
) -> float:
    """
    Calculates the confidence level based on sample statistics.

    This function is the inverse of the `sample_size` function.

    Args:
        sample_size: The size of the sample.
        population_size: The total size of the population.
        confidence_interval: The confidence interval (margin of error).
                             Default is 0.02 (2%).

    Returns:
        The calculated confidence level as a float (e.g., 0.95 for 95%).
    """
    if sample_size >= population_size:
        return 1.0

    # For sample size calculation, we assume the worst-case variance, where p=0.5
    p = 0.5
    # This is the inverse calculation of Cochran's formula for finite populations
    # to find the sample size for an infinite population (n_0).
    n_0 = (sample_size * (population_size - 1)) / (population_size - sample_size)
    # From n_0, we can calculate the square of the z-score.
    z_squared = n_0 * (confidence_interval**2) / (p * (1 - p))
    if z_squared < 0:
        # This case should not be reached with valid inputs (n < N).
        return 0.0
    z_score = math.sqrt(z_squared)

    # Convert z-score back to confidence level: 2 * cdf(z) - 1
    confidence = 2 * st.norm.cdf(z_score) - 1
    return confidence
