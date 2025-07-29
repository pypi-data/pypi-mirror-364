class Dot:
    __slots__ = ("_data",)

    def __init__(self, d: dict | None = None, **kwargs):
        self._data = {}
        if d is not None:
            if isinstance(d, Dot):
                d = d.to_dict()
            for k, v in d.items():
                self[k] = v
        for k, v in kwargs.items():
            self[k] = v

    def _wrap(self, v):
        if isinstance(v, dict):
            return Dot(v)
        return v

    def __getattr__(self, key):
        try:
            return self._data[key]
        except KeyError:
            d = Dot()
            self._data[key] = d
            return d

    def __setattr__(self, key, value):
        if key == "_data":
            super().__setattr__(key, value)
        else:
            self._data[key] = self._wrap(value)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = self._wrap(value)

    def __contains__(self, key):
        return key in self._data

    def to_dict(self):
        result = {}
        for k, v in self._data.items():
            if isinstance(v, Dot):
                v = v.to_dict()
            result[k] = v
        return result

    def __repr__(self):
        return f"Dot({self.to_dict()})"

    def copy(self):
        return Dot(self.to_dict())

    def merge(self, other):
        for k, v in other.to_dict().items():
            if (
                k in self._data
                and isinstance(self._data[k], Dot)
                and isinstance(v, dict)
            ):
                self._data[k].merge(Dot(v))
            else:
                self._data[k] = self._wrap(v)
