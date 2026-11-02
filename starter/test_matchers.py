"""Final Selection test.  Run:  python test_matchers.py
Every line must say PASS before you leave for your first mission."""
from matchers import *

CASES = [("ababa", "aba", [0, 2]),
         ("abababacaba", "ababaca", [2]),
         ("aaaaaa", "aa", [0, 1, 2, 3, 4]),
         ("acaabcaabcab", "abcab", [7]),
         ("abcabcabc", "d", [])]

def check(name, got, expected):
    print(("PASS " if got == expected else "FAIL ") + name, "" if got == expected else f"-> got {got}, expected {expected}")

for T, P, exp in CASES:
    check(f"naive       {P} in {T}", naive_match(T, P)[0], exp)
    check(f"rabin-karp  {P} in {T}", rabin_karp_match(T, P)[0], exp)
    check(f"kmp         {P} in {T}", kmp_match(T, P)[0], exp)
    delta = compute_transition_function(P, set(T) | set(P))
    check(f"automaton   {P} in {T}", fa_match(T, delta, len(P))[0], exp)

check("prefix function of ababaca", compute_prefix_function("ababaca"), [0, 0, 1, 2, 3, 0, 1])
r = rabin_karp_match("3141592653589793", "26", d=10, q=11)
check("rabin-karp shifts with d=10, q=11", r[0], [6])
check("rabin-karp spurious hits with d=10, q=11", r[2], 3)

# a caw split across two chunks must still be heard
pi = compute_prefix_function("KAKAKA")
q, s1, _ = kmp_resume("xxKAKA", "KAKAKA", pi, 0, 0)
q, s2, _ = kmp_resume("KAyy", "KAKAKA", pi, q, 6)
check("kmp_resume across a chunk boundary", s1 + s2, [2])
