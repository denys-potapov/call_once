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
print(fib(100000) % 1000)
