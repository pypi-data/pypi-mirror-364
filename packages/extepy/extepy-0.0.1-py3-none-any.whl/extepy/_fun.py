from functools import wraps

from ._seq import cycleperm as _cycleperm, swap as _swap


def cycleperm(cycle=()):
    """Callable that swaps position parameters according to cyclc notation.

    Parameters:
        cycle (list | tuple): List of indices to swap.

    Returns:
        Callable[callable, callable]: a callable that swaps a callable so that
            its arguments are swapped according to cycle notation.

    Examples:

        Permutate a function.

        >>> permed = cycleperm(cycle=[0, 1])(pow)
        >>> permed(3, 2)
        8

        Use as a decorator.

        >>> @cycleperm(cycle=[0, 1])
        ... def g(a, b):
        ...    return (a + b) * (a - b)
        >>> g(2, 3)
        5
    """
    def wrapper(f):

        @wraps(f)
        def fun(*args, **kwargs):
            args = _cycleperm(list(args), cycle=cycle)
            result = f(*args, **kwargs)
            return result
        return fun

    return wrapper


def swap(i=0, j=1):
    """Callable that swaps positional arguments in a pair.

    Parameters:
        i (int): Index of the argument to swap.
        j (int): Index of another argument to swap.

    Returns:
        Callable[callable, callable]: a callable that swaps a callable so that two designated arguments are swapped.

    Examples:

        Swap arguments of a callable:

        >>> swapped = swap(i=0, j=1)(pow)
        >>> swapped(3, 2)
        8

        Use as a decorator.

        >>> @swap()
        ... def g(a, b):
        ...     return (a + b) * (a - b)
        >>> g(2, 3)
        5
    """
    def wrapper(f):
        @wraps(f)
        def fun(*args, **kwargs):
            args = _swap(list(args), i=i, j=j)
            result = f(*args, **kwargs)
            return result
        return fun
    return wrapper


def pack(f):
    """Merge all positional arguments of a function to a single tuple argument

    Parameters:
        f (callable):

    Returns:
        callable:

    Examples:

        Apply on a function.

        >>> packed = pack(isinstance)
        >>> packed([1.0, float])
        True

        Use as a decorator.

        >>> import math
        >>> @pack
        ... def g(*args):
        ...    return sum(arg + 1 for arg in args)
        >>> g([1, 2, 3])
        9
    """
    def fun(args, **kwargs):
        result = f(*args, **kwargs)
        return result
    return fun


def unpack(f):
    """Replace a single tuple/list argument to many positional arguments.

    Parameters:
        f (callable):

    Returns:
        callable:

    Examples:

        Apply on a function.

        >>> unpacked = unpack(all)
        >>> unpacked(True, True, True)
        True

        Use as decorator.

        >>> @unpack
        ... def g(values):
        ...    return max(values) - min(values)
        >>> g(1, 2, 3)
        2
    """
    def fun(*args, **kwargs):
        result = f(args, **kwargs)
        return result
    return fun


def skewer(*callables):
    """Composite multiple callables into one callable.

    Parameters:
        *callables (callable):

    Returns:
        callable: A callable that calls all callables in order.

    Examples:
        >>> def minmax(x, y):
        ...     return min(x, y), max(x, y)
        >>> def mul(x, y):
        ...     return x * y
        >>> skewered = skewer(minmax, mul)
        >>> skewered(5, 3)
        15
    """
    def fun(*args, **kwargs):
        result = args
        for callable in callables:
            if isinstance(result, tuple):
                result = callable(*result, **kwargs)
            else:
                result = callable(result, **kwargs)
        return result
    return fun


def repeat(n=1):
    """Repeat a callable n times.

    Parameters:
        n (int): Number of times to repeat.

    Returns:
        Callable[callable, callable]: a callable that swaps a callable so that it is called n times.

    Examples:

        Apply on a function.

        >>> repeated = repeat(n=2)(abs)
        >>> repeated(-3)
        3

        Use as a decorator.

        >>> @repeat(n=2)
        ... def g(a):
        ...     return a + 1
        >>> g(1)
        3
    """
    def wrapper(f):
        callables = [f] * n

        @wraps(f)
        def fun(*args, **kwargs):
            skewed = skewer(*callables)
            result = skewed(*args, **kwargs)
            return result
        return fun
    return wrapper
