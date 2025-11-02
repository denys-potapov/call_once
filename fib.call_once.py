fib_CACHE = {}


def fib(*args, **kwargs):
    key = (args, tuple(kwargs.items()))
    if key not in fib_CACHE:
        fib_CACHE[key] = fib_aux(*args, **kwargs)
    return fib_CACHE[key]


def fib_aux(n):
    if n <= 1:
        return ("result", n)
    f1 = fib(n - 1)
    f2 = fib(n - 2)
    return ("result", f1 + f2)


print(fib(1000000))
