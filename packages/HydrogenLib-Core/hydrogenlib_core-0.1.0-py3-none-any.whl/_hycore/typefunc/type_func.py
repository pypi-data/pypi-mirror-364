import inspect


def get_subclasses(cls):
    """
    获取所有子类
    """
    if cls is type:
        return []
    return cls.__subclasses__()


def get_subclass_counts(cls):
    """
    获取所有子类的数量
    """
    if cls is type:
        return 0
    return len(cls.__subclasses__())


def get_subclasses_recursion(cls):
    """
    递归地获取所有子类
    """
    if cls is type:
        return []
    return (
            cls.__subclasses__() + [g for s in cls.__subclasses__() for g in get_subclasses_recursion(s)]
    )


def get_subclass_counts_recursion(cls):
    """
    获取所有子类的数量
    """
    if cls is type:
        return 0
    return len(cls.__subclasses__()) + sum(get_subclass_counts_recursion(s) for s in cls.__subclasses__())


def iter_annotations(obj, *, globals=None, locals=None, eval_str=False):
    """
    迭代对象中的所有注解
    """
    for name, typ in inspect.get_annotations(obj, globals=globals, locals=locals, eval_str=eval_str).items():
        yield name, typ, getattr(obj, name, None)


def iter_attributes(obj):
    """
    迭代对象中的所有属性
    """
    for name in dir(obj):
        if name.startswith("_"):
            continue
        yield name, getattr(obj, name)
