from collections import namedtuple
FieldLen = namedtuple('FieldLen', 'min max exact')
NAME_FIELD = FieldLen(5, 100, 0)