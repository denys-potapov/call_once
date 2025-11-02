# calculate fibonacci number
@call_once
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)


print(fib(100_000) % 1_000)
