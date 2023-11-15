"""Decompress CoDICE science data.

For CoDICE, there are 3 forms of compression:
    1. Table-based lossy compression A (24- or 32-bit -> 8-bit)
    2. Table-based lossy compression B (24- or 32-bit -> 8 bit)
    3. LZMA lossless compression

Only one lossy option can be selected in cases of lossy + lossless compression.
Thus, there are 6 possibly compression algorithms:
    1. No compression
    2. Lossy A only
    3. Lossy B only
    4. Lossless only
    5. Lossy A + lossless
    6. Lossy B + lossless

In the case of (5) and (6), the data is first run through lossy compression, and
then the result is run through lossless compression. Thus, to decompress, one
must apply lossless decompression first, then lossy decompression

References
----------
    This information was provided via email from Greg Dunn on Oct 23, 2023
"""

import lzma

from imap_processing.codice.constants import LOSSY_A_TABLE, LOSSY_B_TABLE


def _apply_lossy_a(compressed_value):
    """Apply 8-bit to 32-bit Lossy A decompression algorithm.

    The Lossy A algorithm uses a lookup table imported into this module.

    Parameters
    ----------
    compressed_value : int
        The compressed 8-bit value

    Returns
    -------
    int
        The 24- or 32-bit decompressed value
    """
    return LOSSY_A_TABLE[compressed_value]


def _apply_lossy_b(compressed_value):
    """Apply 8-bit to 32-bit Lossy B decompression algorithm.

    The Lossy B algorithm uses a lookup table imported into this module.

    Parameters
    ----------
    compressed_value : int
        The compressed 8-bit value

    Returns
    -------
    int
        The 24- or 32-bit decompressed value
    """
    return LOSSY_B_TABLE[compressed_value]


def _apply_lzma_lossless(compressed_value):
    """Apply LZMA lossless decompression algorithm.

    Parameters
    ----------
    compressed_value : int
        The compressed 8-bit value

    Returns
    -------
    decompressed_value : int
        The 24- or 32-bit decompressed value
    """
    decompressed_value = lzma.decompress(compressed_value)
    decompressed_value = int.from_bytes(decompressed_value, byteorder="big")

    return decompressed_value


def decompress(compressed_value, algorithm):
    """Decompress the value.

    Apply the appropriate decompression algorithm(s) based on the value
    of the ``algorithm`` attribute. One or more individual algorithms may be
    applied to a given compressed value.

    Parameters
    ----------
    compressed_value : int
        The 8-bit compressed value to decompress
    algorithm : str
        The algorithm to apply. Supported algorithms include 'no compression',
        'lossyA', 'lossyB', 'lossless', 'lossyA+lossless', and 'lossyB+lossless'

    Returns
    -------
    decompressed_value : int
        The 24- or 32-bit decompressed value
    """
    if algorithm == "no compression":
        decompressed_value = compressed_value
    elif algorithm == "lossyA":
        decompressed_value = _apply_lossy_a(compressed_value)
    elif algorithm == "lossyB":
        decompressed_value = _apply_lossy_b(compressed_value)
    elif algorithm == "lossless":
        decompressed_value = _apply_lzma_lossless(compressed_value)
    elif algorithm == "lossyA+lossless":
        decompressed_value = _apply_lzma_lossless(compressed_value)
        decompressed_value = _apply_lossy_a(decompressed_value)
    elif algorithm == "lossyB+lossless":
        decompressed_value = _apply_lzma_lossless(compressed_value)
        decompressed_value = _apply_lossy_b(decompressed_value)
    else:
        raise ValueError(f"{algorithm} is not supported")

    return decompressed_value
