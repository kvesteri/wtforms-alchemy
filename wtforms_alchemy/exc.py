class UnknownTypeException(Exception):
    def __init__(self, column):
        Exception.__init__(
            self,
            "Unknown type '%r' for column '%s'" %
            (column.type, column.name)
        )


class InvalidAttributeException(Exception):
    def __init__(self, attr_name):
        Exception.__init__(
            self,
            "Model does not contain attribute named '%s'." %
            attr_name
        )


class AttributeTypeException(Exception):
    def __init__(self, attr_name):
        Exception.__init__(
            self,
            "Model attribute '%s' is not of type ColumnProperty." %
            attr_name
        )


class UnknownConfigurationOption(Exception):
    def __init__(self, option):
        Exception.__init__(
            self,
            "Unknown configuration option '%s' given." %
            option
        )
