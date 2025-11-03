import sys
import pprint

def call_once(fn, args, cache):
    stack = {}

    def push(args):
        stack[args] = None

    def pop():
        return stack.popitem()[0]
    push(args)
    while len(stack) > 0:
        current_args = pop()
        if current_args in cache:
            continue
        (posargs, kwargs) = current_args
        (typ, value) = fn(*posargs, **dict(kwargs))
        if typ == 'call':
            push(current_args)
            push(value)
            continue
        if typ == 'result':
            cache[current_args] = value
    return cache[args]

def solve(CaseN):
    _Т = in_int()
    A = tuple(in_ints())
    min_left_CACHE = {}

    def min_left(*posargs, **kwargs):
        args = (posargs, tuple(kwargs.items()))
        return call_once(min_left_aux, args, min_left_CACHE)

    def min_left_aux(n):
        from_ground = A[n]
        if n == 0:
            return ('result', from_ground)
        else:
            dist = abs(A[n] - A[n - 1])
            min_left_0_args = ((n - 1,), ())
            if min_left_0_args not in min_left_CACHE:
                return ('call', min_left_0_args)
            min_left_0 = min_left_CACHE[min_left_0_args]
            from_left = max(min_left_0, dist)
            return ('result', min(from_ground, from_left))
    min_right_CACHE = {}

    def min_right(*posargs, **kwargs):
        args = (posargs, tuple(kwargs.items()))
        return call_once(min_right_aux, args, min_right_CACHE)

    def min_right_aux(n):
        from_ground = A[n]
        if n == len(A) - 1:
            return ('result', from_ground)
        else:
            dist = abs(A[n] - A[n + 1])
            min_right_0_args = ((n + 1,), ())
            if min_right_0_args not in min_right_CACHE:
                return ('call', min_right_0_args)
            min_right_0 = min_right_CACHE[min_right_0_args]
            from_right = max(min_right_0, dist)
            return ('result', min(from_ground, from_right))
    mn = 0
    for i in range(len(A)):
        min_from_both = min(min_left(i), min_right(i))
        mn = max(mn, min_from_both)
    return mn

def in_int():
    return int(input())

def in_ints():
    return list(map(int, input().split()))
if __name__ == '__main__':
    T = in_int()
    for C in range(1, T + 1):
        R = solve(C)
        print('Case #' + str(C) + ': ' + str(R))
