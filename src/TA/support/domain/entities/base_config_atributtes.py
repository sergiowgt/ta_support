from collections import namedtuple
FieldLen = namedtuple('FieldLen', 'min max exact')

NAME_FIELD = FieldLen(5, 100, 0)
UUID_FIELD = FieldLen(0, 0, 36)
CPF_FIELD = FieldLen(0, 0, 11)
CNPJ_FIELD = FieldLen(0, 0, 14)
NAME_FIELD = FieldLen(0, 100, 0)
CREATE_BY_FIELD = FieldLen(0, 50, 0)
UPDATE_BY_FIELD = FieldLen(0, 50, 0)
STATECODE_FIELD = FieldLen(0, 0, 2)
