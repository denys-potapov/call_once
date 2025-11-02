# call_once
python macro for deep recursion

```
    python3 call_once.py < fib.py > fib.call_once.py
```

## Sample

```python
@call_once
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

It replaces recursive call `fib(n - 1)` with following code

```
    fib_0_args = (n - 1)
    if fib_0_args not in fib_CACHE:
        return ('call', fib_0_args)
    fib_0 = fib_CACHE[fib_0_args]
```

1. Check if function has already been called. Then  - use it return value.
2. If not return 'call'. That will tell `call_once` loop that we need to call the function with args.
