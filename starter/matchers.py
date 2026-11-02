"""
Demon Slayer Corps — The String Hunt
Your four techniques (matchers). Fill in every function marked TODO,
following the pseudocode from Lectures 7, 8 and 9.

Rules:
  * Shifts are 0-based: P occurs with shift s if T[s:s+m] == P.
  * Do NOT use str.find, the `in` operator on strings, str.count, re, or any other
    built-in search inside these functions. Compare characters one by one.
  * "comparisons" = how many times you compare one character of T with one character of P.

Check your work with:  python test_matchers.py
"""


def naive_match(T, P):
    """Lecture 7. Slide P over T one position at a time.
    Returns (shifts, comparisons)."""
    n = len(T)
    m = len(P)
    shifts = []
    comparisons = 0

    for s in range(n - m + 1):
        j = 0
        while j < m:
            comparisons += 1  # one char of T vs one char of P
            if T[s + j] != P[j]:
                break  # mismatch, slide to the next shift
            j += 1
        if j == m:  # made it all the way through P
            shifts.append(s)

    return shifts, comparisons


def rabin_karp_match(T, P, d=256, q=101):
    """Lecture 7. Use ord(ch) as the digit value of a character.
    On every hash hit, verify character by character.
    Returns (shifts, comparisons, spurious_hits)."""
    n = len(T)
    m = len(P)
    shifts = []
    comparisons = 0
    spuriousHits = 0

    if m > n:  # pattern longer than text, nothing to find
        return shifts, comparisons, spuriousHits

    h = pow(d, m - 1, q)  # d^(m-1) mod q, used to remove the leading digit
    pHash = 0
    tHash = 0

    # hash of P and of the first window of T
    for i in range(m):
        pHash = (d * pHash + ord(P[i])) % q
        tHash = (d * tHash + ord(T[i])) % q

    for s in range(n - m + 1):
        if pHash == tHash:
            # hash hit, verify char by char
            j = 0
            while j < m:
                comparisons += 1
                if T[s + j] != P[j]:
                    break
                j += 1
            if j == m:
                shifts.append(s)
            else:
                spuriousHits += 1  # hash matched but the text didn't

        # roll the hash to the next window (drop T[s], add T[s+m])
        if s < n - m:
            tHash = (d * (tHash - ord(T[s]) * h) + ord(T[s + m])) % q

    return shifts, comparisons, spuriousHits


def compute_prefix_function(P):
    """Lecture 8. Returns the list pi, where pi[i] is the length of the longest
    proper prefix of P[0..i] that is also a suffix of it.
    Example: compute_prefix_function("ababaca") == [0, 0, 1, 2, 3, 0, 1]"""
    m = len(P)
    pi = [0] * m
    k = 0  # length of the current matched prefix

    for i in range(1, m):
        while k > 0 and P[k] != P[i]:
            k = pi[k - 1]  # fall back to the next best prefix
        if P[k] == P[i]:
            k += 1
        pi[i] = k

    return pi


def kmp_resume(T, P, pi, q, offset):
    """Lecture 8, with one change: the matcher starts in state q instead of 0,
    and `offset` is the position of T[0] inside the whole file.
    This lets you feed a big file in chunks and carry q from one chunk to the next.
    After a full match, set q = pi[q - 1] so overlapping matches are found.
    Returns (q_at_the_end, shifts_found, comparisons)."""
    n = len(T)
    m = len(P)
    shifts = []
    comparisons = 0

    for i in range(n):
        # on a mismatch, fall back using pi
        while q > 0 and P[q] != T[i]:
            comparisons += 1
            q = pi[q - 1]

        comparisons += 1  # the compare that ends the loop (match, or q is 0)
        if P[q] == T[i]:
            q += 1

        if q == m:
            shifts.append(offset + i - m + 1)  # offset makes the shift global
            q = pi[q - 1]  # keep going so overlaps are found

    return q, shifts, comparisons


def kmp_match(T, P):
    """Whole-text KMP. Already done for you: it just calls kmp_resume once."""
    pi = compute_prefix_function(P)
    _, shifts, comparisons = kmp_resume(T, P, pi, 0, 0)
    return shifts, comparisons


def compute_transition_function(P, alphabet):
    """Lecture 9. Returns delta as a list of dicts: delta[q][a] = next state.
    There are len(P) + 1 states (0 .. m)."""
    m = len(P)
    delta = []

    for q in range(m + 1):
        row = {}
        for a in alphabet:
            # biggest k such that P[0..k) is a suffix of P[0..q) + a
            k = min(m, q + 1)
            while k > 0:
                same = True
                for j in range(k):
                    pos = q + 1 - k + j  # position inside P[0..q) + a
                    if pos == q:
                        ch = a  # the extra char at the end
                    else:
                        ch = P[pos]
                    if P[j] != ch:
                        same = False
                        break
                if same:
                    break
                k -= 1
            row[a] = k
        delta.append(row)

    return delta


def fa_match(T, delta, m):
    """Lecture 9. Start at q = 0 and do q = delta[q][T[i]] for every character.
    A character not in the alphabet sends you back to state 0.
    Returns (shifts, steps) where steps = number of table lookups."""
    shifts = []
    steps = 0
    q = 0

    for i in range(len(T)):
        steps += 1  # one table lookup
        q = delta[q].get(T[i], 0)  # not in alphabet -> back to 0
        if q == m:
            shifts.append(i - m + 1)

    return shifts, steps
