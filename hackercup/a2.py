# Problem A2: Snake Scales (Chapter 2)
#
# https://www.facebook.com/codingcompetitions/hacker-cup/2025/round-1/problems/A2
import sys
import pprint


def call_once(func):
    return func


def solve(CaseN):
    _Т = in_int()
    A = tuple(in_ints())

    @call_once
    def min_left(n):
        from_ground = A[n]
        if n == 0:
            return from_ground
        else:
            dist = abs(A[n] - A[n - 1])
            from_left = max(min_left(n - 1), dist)
            return min(from_ground, from_left)

    @call_once
    def min_right(n):
        from_ground = A[n]
        if n == len(A) - 1:
            return from_ground
        else:
            dist = abs(A[n] - A[n + 1])
            from_right = max(min_right(n + 1), dist)
            return min(from_ground, from_right)

    mn = 0
    for i in range(len(A)):
        min_from_both = min(min_left(i), min_right(i))
        mn = max(mn, min_from_both)

    return mn


def in_int():
    return int(input())


def in_ints():
    return list(map(int, input().split()))


if __name__ == "__main__":
    T = in_int()
    for C in range(1, T + 1):
        R = solve(C)
        print("Case #" + str(C) + ": " + str(R))
