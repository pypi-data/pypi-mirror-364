# extepy: Python Programming Tools

## Install

It can be installed with pip.

```shell
pip install --upgrade extepy
```

It works in both Python 2 and Python 3.

## Documentation

Docs: <https://extepy.github.io>

## Extension of `hashlib`

- `extepy.filehash(obj, method="sha256", batchsize=4096)` computes the hash value of a file using the specified hash function.

Example:

```python
>>> from extepy import filehash
>>> filehash("test.txt")
'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
```

## Extension of `importlib`

- `extepy.reload(obj, update_global=True, update_local=True)` provides advanced module and object reloading capabilities for Python, so that developer can modify code without restarting the interpreter.

This function solves key limitations of Python's built-in reloading functionality by:

- Supporting all import styles: `import X`, `from A import X`, and `from A import B as X`
- Automatically updating references without requiring reassignment
- Offering granular control over namespace updates (global and/or local namespace)
- Compatible to both Python 2.6+ and Python 3.1+

Examples:

```python
from extepy import reload

# Direct import
from mymodule import myfunction
reload(myfunction)

# Aliased import
from mymodule import myfunction as myfunction1
reload(myfunction1)

# Module import
import mymodule
reload(mymodule)

# Module by name
reload("mymodule")
```

Example: Automatically updates references without reassignment:

```python
from extepy import reload
from mymodule import myfunction
reload(myfunction)  # Modify myfunction in mymodule.py
print(myfunction([3,1,2]))  # Uses new version
```

Example: Function Reload with Aliases

```python
from extepy import reload
from mymodule import myfunction as myfunction1, myfunction as myfunction2
# ... modify myfunction implementation ...
reload(myfunction1)  # Updates both myfunction1 and myfunction2
```

Example: Selective Namespace Update

```python
from extepy import reload
myfunction = None  # Global reference
def f():
    global myfunction
    from mymodule import myfunction
    reload(myfunction, update_local=False)  # Only update global reference
```

```python
from extepy import reload
def f():
    from mymodule import myfunction
    # ... modify calculator ...
    reload(myfunction, update_global=False)  # Update only the local calc reference
```
