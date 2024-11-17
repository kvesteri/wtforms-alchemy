class UnknownTypeException(Exception):
    def __init__(self, column):
        Exception.__init__(
            self, f"Unknown type '{column.type!r}' for column '{column.name}'"
        )


class InvalidAttributeException(Exception):
    def __init__(self, attr_name):
        Exception.__init__(
            self, f"Model does not contain attribute named '{attr_name}'."
        )


class AttributeTypeException(Exception):
    def __init__(self, attr_name):
        Exception.__init__(
            self, f"Model attribute '{attr_name}' is not of type ColumnProperty."
        )


class UnknownConfigurationOption(Exception):
    def __init__(self, option):
        Exception.__init__(self, f"Unknown configuration option '{option}' given.")
