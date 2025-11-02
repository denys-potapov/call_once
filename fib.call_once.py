import time

def call_once(fn, args, cache):
    stack = {}

    def push(args):
        stack[args] = None

    def pop():
        return stack.popitem()[0]
    push(args)
    while len(stack) > 0:
        current_args = pop()
        (posargs, kwargs) = current_args
        (typ, value) = fn(*posargs, **dict(kwargs))
        if typ == 'call':
            push(current_args)
            push(value)
            continue
        if typ == 'result':
            cache[current_args] = value
    return cache[args]
fib_CACHE = {}

def fib(*posargs, **kwargs):
    args = (posargs, tuple(kwargs.items()))
    return call_once(fib_aux, args, fib_CACHE)

def fib_aux(n):
    if n <= 1:
        return ('result', n)
    fib_0_args = ((n - 1,), ())
    if fib_0_args not in fib_CACHE:
        return ('call', fib_0_args)
    fib_0 = fib_CACHE[fib_0_args]
    fib_1_args = ((n - 2,), ())
    if fib_1_args not in fib_CACHE:
        return ('call', fib_1_args)
    fib_1 = fib_CACHE[fib_1_args]
    return ('result', fib_0 + fib_1)

def fib_fast(n):
    lst = [0] * (n + 1)
    lst[0] = 0
    lst[1] = 1
    for i in range(2, n + 1):
        lst[i] = lst[i - 1] + lst[i - 2]
    return lst[n]
start = time.time()
result = fib_fast(200000) % 1000
end = time.time()
print(f'fib_fast time: {end - start:.2f} seconds. Result {result}')
start = time.time()
result = fib(200000) % 1000
end = time.time()
print(f'@call_once fib time: {end - start:.2f} seconds. Result {result}')
