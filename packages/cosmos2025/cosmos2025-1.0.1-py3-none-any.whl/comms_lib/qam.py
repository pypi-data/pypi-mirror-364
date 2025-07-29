import numpy as np


def detect_qam(symbols: np.ndarray, M: int) -> np.ndarray:
    constellation = qam_constellation(M)
    distances = np.abs(symbols[:, None] - constellation[None, :])
    return constellation[np.argmin(distances, axis=1)]


def qam_constellation(M: int = 4) -> np.ndarray:
    """Generates random QAM constellation symbols from a square QAM constellation normalized to unit average symbol energy.

    Args:
        M (int): Order of the QAM constellation (e.g., 4 for QPSK, 16 for 16-QAM).
            Default is 4 (QPSK).

    Returns:
        np.ndarray: Array of `M`-QAM constellation points, centered around the origin and normalized to unit average symbol energy.
    """

    # check if M is a valid QAM order
    if not np.sqrt(M).is_integer() or M < 2:
        raise ValueError("M is not a valid QAM order.")

    # Generate constellation points
    constellation = np.array(
        [x + 1j * y for x in range(int(np.sqrt(M))) for y in range(int(np.sqrt(M)))]
    )
    constellation -= constellation.mean()  # Center constellation around origin
    constellation /= np.sqrt((np.abs(constellation) ** 2).mean())
    return constellation


def gen_rand_qam_symbols(N: int, M: int = 4) -> np.ndarray:
    """Generates random QAM constellation symbols from a square QAM constellation normalized to unit average symbol energy.

    Args:
        N (int): Number of symbols to generate.
        M (int): Order of the QAM constellation (e.g., 4 for QPSK, 16 for 16-QAM).
            Default is 4 (QPSK).

    Returns:
        np.ndarray: Array of randomly selected `M`-QAM symbols.
    """
    # Generate random symbols
    return np.random.default_rng().choice(qam_constellation(M), size=N, replace=True)
