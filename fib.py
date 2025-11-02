import time


def call_once(func):
    # placeholder will be replaced by actual code
    return func


# calculate fibonacci number
@call_once
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)


def fib_fast(n):
    lst = [0] * (n + 1)
    lst[0] = 0
    lst[1] = 1
    for i in range(2, n + 1):
        lst[i] = lst[i - 1] + lst[i - 2]
    return lst[n]


start = time.time()
result = fib_fast(200_000) % 1_000
end = time.time()
print(f"fib_fast time: {end - start:.2f} seconds. Result {result}")

start = time.time()
result = fib(200_000) % 1_000
end = time.time()
print(f"@call_once fib time: {end - start:.2f} seconds. Result {result}")
