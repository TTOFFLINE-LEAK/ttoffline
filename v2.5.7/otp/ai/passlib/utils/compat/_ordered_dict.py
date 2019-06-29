try:
    from thread import get_ident as _get_ident
except ImportError:
    from dummy_thread import get_ident as _get_ident

class OrderedDict(dict):

    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        try:
            self.__root
        except AttributeError:
            self.__root = root = []
            root[:] = [
             root, root, None]
            self.__map = {}

        self.__update(*args, **kwds)
        return

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        if key not in self:
            root = self.__root
            last = root[0]
            last[1] = root[0] = self.__map[key] = [last, root, key]
        dict_setitem(self, key, value)

    def __delitem__(self, key, dict_delitem=dict.__delitem__):
        dict_delitem(self, key)
        link_prev, link_next, key = self.__map.pop(key)
        link_prev[1] = link_next
        link_next[0] = link_prev

    def __iter__(self):
        root = self.__root
        curr = root[1]
        while curr is not root:
            yield curr[2]
            curr = curr[1]

    def __reversed__(self):
        root = self.__root
        curr = root[0]
        while curr is not root:
            yield curr[2]
            curr = curr[0]

    def clear(self):
        try:
            for node in self.__map.itervalues():
                del node[:]

            root = self.__root
            root[:] = [root, root, None]
            self.__map.clear()
        except AttributeError:
            pass

        dict.clear(self)
        return

    def popitem(self, last=True):
        if not self:
            raise KeyError('dictionary is empty')
        root = self.__root
        if last:
            link = root[0]
            link_prev = link[0]
            link_prev[1] = root
            root[0] = link_prev
        else:
            link = root[1]
            link_next = link[1]
            root[1] = link_next
            link_next[0] = root
        key = link[2]
        del self.__map[key]
        value = dict.pop(self, key)
        return (
         key, value)

    def keys(self):
        return list(self)

    def values(self):
        return [ self[key] for key in self ]

    def items(self):
        return [ (key, self[key]) for key in self ]

    def iterkeys(self):
        return iter(self)

    def itervalues(self):
        for k in self:
            yield self[k]

    def iteritems(self):
        for k in self:
            yield (k, self[k])

    def update(*args, **kwds):
        if len(args) > 2:
            raise TypeError('update() takes at most 2 positional arguments (%d given)' % (
             len(args),))
        else:
            if not args:
                raise TypeError('update() takes at least 1 argument (0 given)')
        self = args[0]
        other = ()
        if len(args) == 2:
            other = args[1]
        if isinstance(other, dict):
            for key in other:
                self[key] = other[key]

        else:
            if hasattr(other, 'keys'):
                for key in other.keys():
                    self[key] = other[key]

            else:
                for key, value in other:
                    self[key] = value

        for key, value in kwds.items():
            self[key] = value

    __update = update
    __marker = object()

    def pop(self, key, default=__marker):
        if key in self:
            result = self[key]
            del self[key]
            return result
        if default is self.__marker:
            raise KeyError(key)
        return default

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        self[key] = default
        return default

    def __repr__(self, _repr_running={}):
        call_key = (
         id(self), _get_ident())
        if call_key in _repr_running:
            return '...'
        _repr_running[call_key] = 1
        try:
            if not self:
                return '%s()' % (self.__class__.__name__,)
            return '%s(%r)' % (self.__class__.__name__, self.items())
        finally:
            del _repr_running[call_key]

    def __reduce__(self):
        items = [ [k, self[k]] for k in self ]
        inst_dict = vars(self).copy()
        for k in vars(OrderedDict()):
            inst_dict.pop(k, None)

        if inst_dict:
            return (self.__class__, (items,), inst_dict)
        return (self.__class__, (items,))

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value

        return d

    def __eq__(self, other):
        if isinstance(other, OrderedDict):
            return len(self) == len(other) and self.items() == other.items()
        return dict.__eq__(self, other)

    def __ne__(self, other):
        return not self == other