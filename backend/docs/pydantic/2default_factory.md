Checklist
- Explain what kinds of callables `default_factory` accepts
- Give examples besides `lambda`
- Show the common patterns you can use in Python

Yes — `default_factory` can use **any callable**, not just `lambda` or `list`.

## What `default_factory` accepts
It accepts a function or callable object that:
- takes **no arguments**
- returns the default value

---

## Examples of valid callables

### 1) Built-in function
```python
from pydantic import BaseModel, Field

class M(BaseModel):
    tags: list[str] = Field(default_factory=list)
```

### 2) Named function
```python
def make_false():
    return False

class M(BaseModel):
    supports_thinking: bool = Field(default_factory=make_false)
```

### 3) Another built-in callable
```python
from datetime import datetime

class M(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 4) Callable class instance
```python
class Counter:
    def __call__(self):
        return 123

class M(BaseModel):
    x: int = Field(default_factory=Counter())
```

---

## Important rule
The callable must be **callable with no arguments**:

```python
Field(default_factory=some_function)   # OK if some_function() takes no args
```

This is **not** okay if it needs arguments:

```python
def make_value(x):   # needs an argument
    return x

Field(default_factory=make_value)  # error
```

---

## For your case
For a boolean default, you usually do **not** need `default_factory` at all:

```python
supports_thinking: bool = Field(False, description="Whether the model supports thinking")
```

That is the simplest and most common choice.

If you want, I can show you a quick table of **when to use `default`, `default_factory`, or `lambda`**.