from typing import List


def primes(start: int = 2, limit: int = None) -> List[int]:
    """
    Efficiently generate all prime numbers between start and limit using the Sieve of Eratosthenes algorithm.

    Args:
        start (int): The lower bound for finding prime numbers (inclusive). Defaults to 2.
        limit (int): The upper bound for finding prime numbers (inclusive)

    Returns:
        List[int]: A list of all prime numbers from start to the given limit

    Raises:
        ValueError: If limit is less than 2 or start is less than 2

    Examples:
        >>> primes(2, 10)
        [2, 3, 5, 7]
        >>> primes(10, 20)
        [11, 13, 17, 19]
    """
    if limit is None:
        raise ValueError("Limit must be provided")
    if limit < 2:
        raise ValueError("Limit must be at least 2")
    if start < 2:
        raise ValueError("Start must be at least 2")
    if start > limit:
        return []

    if limit < 3:
        all_primes = [2]
    else:
        size = (limit // 2) + 1
        is_prime = bytearray(size)
        is_prime[:] = b"\x01" * size
        is_prime[0] = 0

        sqrt_limit = int(limit**0.5) // 2 + 1

        for i in range(1, sqrt_limit):
            if is_prime[i]:
                start_idx = 2 * i * (i + 1)
                for j in range(start_idx, size, 2 * i + 1):
                    is_prime[j] = 0

        all_primes = [2]
        all_primes.extend(2 * i + 1 for i in range(1, size) if is_prime[i])

    return [p for p in all_primes if p >= start]
