class UnknownTypeException(Exception):
    def __init__(self, column):
        Exception.__init__(
            self,
            "Unknown type '%s' for column '%s'" %
            (column.type, column.name)
        )


class InvalidAttributeException(Exception):
    def __init__(self, attr_name):
        Exception.__init__(
            self,
            "Model does not contain attribute named '%s'." %
            attr_name
        )


class UnknownIdentityException(Exception):
    pass
