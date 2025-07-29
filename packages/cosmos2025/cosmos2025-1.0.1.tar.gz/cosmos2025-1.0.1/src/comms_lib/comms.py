"""Helper functions for end-to-end communication with Pluto SDR."""

import matplotlib.pyplot as plt
import numpy as np

from .pulse import get_rrc_pulse, pulse_shape
from .qam import gen_rand_qam_symbols, qam_constellation
from .sequence import zadoff_chu_sequence


def estimate_cfo(received_signal: np.ndarray, seq_num: int, seq_len: int, Ts: float):
    """Estimate coarse CFO from the STF/LTF portion of a received signal.

    Args:
        received_signal (np.ndarray): The received complex baseband samples
            containing the entire STF or LTF (should contain at least K * N samples).
        seq_num (int): Total number of sequence repetitions in STF or LTF.
        seq_len (int): Length of each repeated sequence in samples.
        Ts (float): Sampling period in seconds.

    Returns:
        float: Estimated coarse carrier frequency offset (Hz).

    Raises:
        ValueError: If seq_num < 2 (need at least 2 repetitions to form 1 pair for CFO estimation).
        AssertionError: If signal is too short for given seq_num and seq_len.
    """
    if seq_num < 2:
        raise ValueError(
            "Need at least 2 repetitions to form 1 pair for CFO estimation"
        )

    # Need K repeated segments → (K - 1) pairs
    assert (
        len(received_signal) >= seq_num * seq_len
    ), "Signal too short for given seq_num and seq_len"

    acc = 0.0 + 0.0j
    for k in range(seq_num - 1):  # Now we form (K - 1) pairs
        r1 = received_signal[k * seq_len : (k + 1) * seq_len]
        r2 = received_signal[(k + 1) * seq_len : (k + 2) * seq_len]
        acc += np.vdot(r1, r2)

    angle = np.angle(acc)
    f_cfo = angle / (2 * np.pi * seq_len * Ts)

    return f_cfo


class CommSystem:
    """Class for handling end-to-end communication with Pluto SDR."""

    def __init__(self):
        """Initialize default parameters."""
        self.stf_len: int = 31
        self.ltf_len: int = 937
        self.stf_num: int = 16
        self.ltf_num: int = 2
        self.q: int = 1
        self.beta: float = 0.5
        self.span: int = 20
        self.sps: float = 10
        # Number of data symbols to transmit for each frame
        self.symbols_len: int = 1000

    def __repr__(self):
        return f"""Digital communication system with following parameters:
        stf_len:    {self.stf_len}, length of short training sequence
        ltf_len:    {self.ltf_len}, length of long training sequence
        stf_num:    {self.stf_num}, number of short training sequences
        ltf_num:    {self.ltf_num}, number of long training sequences

        q:          {self.q}, root index for Zadoff-Chu sequence
        beta:       {self.beta}, roll-off factor for pulse shaping
        span:       {self.span}, pulse span in symbols
        sps:        {self.sps}, samples per symbol
        """

    @property
    def pilot_len(self) -> int:
        """Calculate the total length of pilot symbols."""
        return self.stf_len * self.stf_num + self.ltf_len * self.ltf_num

    @property
    def frame_len(self) -> int:
        """Calculate the total frame length."""
        self.pilot_len + self.symbols_len

    def generate_pilot_symbols(self) -> np.ndarray:
        """
        Generate Zadoff-Chu sequence for pilots.

        Returns:
            np.ndarray: Concatenated Zadoff-Chu sequence for STF and LTF.
        """
        stf = zadoff_chu_sequence(self.stf_len, self.q).repeat(self.stf_num)
        ltf = zadoff_chu_sequence(self.ltf_len, self.q).repeat(self.ltf_num)
        return np.concatenate((stf, ltf))
        

    def generate_tx_signal(self, symbols: np.ndarray) -> np.ndarray:
        self.pulse = get_rrc_pulse(self.beta, self.span, self.sps)
        self.pilots = zadoff_chu_sequence(self.ltf_len, self.q)
        syms = np.concatenate((self.pilots, symbols))
        tx_signal = pulse_shape(syms, self.pulse, self.sps)
        return tx_signal
        
    def synchronize(self, signal, pilots: np.ndarray) -> np.ndarray:
        """
        Synchronize the received signal with the known pilot symbols.

        Args:
            signal (np.ndarray): Received signal.
            pilots (np.ndarray): Known pilot symbols for synchronization.

        Returns:
            np.ndarray: Synchronized signal.
        """

        # ========== Symbol synchronization ==========
        conv_len = len(self.pulse) // 2
        start_idx = conv_len        

    def estimate_channel(
        self, pilots: np.ndarray, received_pilots: np.ndarray
    ) -> np.ndarray:
        """
        Estimate the channel response using the received pilot symbols.

        Args:
            pilots (np.ndarray): Known pilot symbols used for channel estimation.
            received_pilots (np.ndarray): Received pilot symbols.

        Returns:
            np.ndarray: Estimated channel response.
        """
        # Use least squares to estimate the channel response
        H = np.linalg.lstsq(pilots[:, np.newaxis], received_pilots, rcond=None)[0]
        return H

    def process_rx_signal(self, received_signal: np.ndarray) -> np.ndarray:
        """
        Process received signal to extract symbols and perform channel equalization.

        Args:
            received_signal (np.ndarray): Received signal after matched filtering.
            pilots (np.ndarray): Known pilot symbols used for channel estimation.

        Returns:
            np.ndarray: Equalized data symbols extracted from the received signal.
        """
        # Generate pulse shape if not already done
        if not hasattr(self, "pulse"):
            self.pulse = self.generate_tx_signal()
        
        # matched filtering
        rx_signal = np.convolve(received_signal, self.pulse, mode="valid") / self.sps

        # Synchronize symbols (timing and frame synchronization)
        downsampled_signal = self.synchronize_symbols(received_signal)
        rx_signal = self.synchronize_frames(downsampled_signal, self.pilots)

        # Extract pilot and data symbols from synchronized signal
        rx_pilots = rx_signal[: self.pilot_len]
        rx_data = rx_signal[self.pilot_len : self.frame_len]

        # Estimate channel using pilots
        H = self.estimate_channel(self.pilots, rx_pilots)

        # Perform channel equalization on data symbols
        equalized_data = rx_data / H

        return equalized_data
