import inspect
import sys
import types


if sys.version_info[0] == 2:  # Python 2
    from imp import reload as _reload
else:  # Python 3
    from importlib import reload as _reload


def reload(obj, update_global=True, update_local=True):
    """Reload objects to pick up the latest implementation.

    Support objects that have been imported via ``import X``, ``from A import X``, or ``from A import B as X``.

    Args:
        obj (types.ModuleType | object | str): The object to reload (module, function, class, or variable)
        update_global (bool): Update references in global namespace (default: True)
        update_local (bool): Update references in local namespace (default: True)
    """
    # Handle module reload such as "import X"
    if isinstance(obj, types.ModuleType):
        reloaded_module = _reload(obj)
        return reloaded_module

    # Get source module information
    module_name = getattr(obj, '__module__', None)
    if not module_name:
        raise TypeError("Object %r has no __module__ attribute" % obj)
    if module_name not in sys.modules:
        raise ImportError("Source module %s not loaded" % module_name)
    module = sys.modules[module_name]

    # Find original attribute name(s)
    attr_names = set()
    for name in dir(module):
        if getattr(module, name, None) is obj:
            attr_names.add(name)
    if not attr_names:
        raise AttributeError("Object %r not found in module %s" % (obj, module_name))

    # Reload the source module
    reloaded_module = _reload(module)

    # Get the new object (use first found attribute)
    new_obj = None
    for name in attr_names:
        if hasattr(reloaded_module, name):
            new_obj = getattr(reloaded_module, name)
            break
    if new_obj is None:
        raise AttributeError("Original attributes missing after reload: %s" % ", ".join(attr_names))

    # Update references in caller's namespace
    if update_global or update_local:
        caller_frame = inspect.currentframe().f_back
        namespaces = []
        if update_global:
            namespaces.append(caller_frame.f_globals)
        if update_local:
            namespaces.append(caller_frame.f_locals)
        for namespace in namespaces:
            for name, value in list(namespace.items()):
                if value is obj:
                    namespace[name] = new_obj

    return new_obj
