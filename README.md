# @call_once

**Unlimited recursion depth for Python functions**

`@call_once` is a Python macro that transforms recursive functions into iterative ones at compile time.
It allows writing clean recursive code without hitting Python’s recursion depth limit.

## Example

```python

# dummy placeholder, so original python file is fully workable
def call_once(func):
    return func

@call_once
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(200_000) % 1_000)
```

This runs safely even for very large recursion depths, limited only by memory.


## Command-line usage

You can also transform files manually:

```bash
python3 call_once.py < fib.py > fib.call_once.py
```

The output file will contain the rewritten, stack-safe version of your function.

## How it works

`@call_once` rewrites recursive functions into an internal loop that:
1. Uses an explicit stack instead of Python’s call stack.
2. Caches intermediate calls so each argument combination executes once.
3. Returns control tokens (`'call'` or `'result'`) to manage flow iteratively.

## Performance

For Fibonacci, runtime is close to iterative code:

```
fib_fast:     1.10 s
@call_once:   1.29 s
```

See [fib.call_once.py](./fib.call_once.py) for details.

## Example use case

Developed during Meta Hacker Cup 2025 to solve deep recursive problems such as [hackercup/a2.py](./hackercup/a2.py), where recursion depth exceeded Python’s limit.
