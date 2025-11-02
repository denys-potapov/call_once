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
