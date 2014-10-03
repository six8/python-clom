PY2 = (str is bytes)
PY3 = (str is not bytes)

if PY3:
    number_types = (int, float)
    integer_types = int
    string_types = str
else:
    number_types = (int, long, float)
    integer_types = (int, long)
    string_types = basestring
