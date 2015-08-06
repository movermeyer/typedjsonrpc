"""Data structures for wrapping methods and information about them."""

from collections import namedtuple

__all__ = ["MethodInfo"]


class MethodInfo(namedtuple("MethodInfo", ["name", "method", "signature"])):
    """An object wrapping a method and information about it.

    :attribute name: Name of the function
    :type name: str
    :attribute method: The function being described
    :type method: function
    :attribute signature: A description of the types this method takes as parameters and returns
    :type signature: MethodSignature or None
    """

    def describe(self):
        """Describes the method.

        :return: Description
        :rtype: dict[str, object]
        """
        return {
            "name": self.name,
            "params": self.parameters,
            "returns": self.return_type,
            "description": self.description,
        }

    @property
    def parameters(self):
        """The parameters for this method in a JSON-compatible format

        :rtype: list[dict[str, str]]
        """
        if self.signature is not None:
            return [{"name": p_name, "type": p_type.__name__}
                    for (p_name, p_type) in self.signature.parameter_types]

    @property
    def return_type(self):
        """The return type for this method in a JSON-compatible format.

        This handles the special case of ``None`` which allows ``type(None)`` also.

        :rtype: str or None
        """
        if self.signature is not None:
            returns = self.signature.return_type
            none_type = type(None)
            if returns is not None and returns is not none_type:
                return returns.__name__

    @property
    def description(self):
        """Returns the docstring for this method.

        :rtype: str
        """
        return self.method.__doc__


class MethodSignature(namedtuple("MethodSignature", ["parameter_types", "return_type"])):
    """Represents the types which a function takes as input and output.

    :attribute parameter_types: A list of tuples mapping strings to type with a specified order
    :type parameter_types: list[str, type]
    :attribute return_type: The type which the function returns
    :type return_type: type
    """

    @staticmethod
    def create(parameter_names, parameter_types, return_type):
        """Returns a signature object ensuring order of parameter names and types.

        :param parameter_names: A list of ordered parameter names
        :type parameter_names: list[str]
        :param parameter_types: A dictionary of parameter names to types
        :type parameter_types: dict[str, type]
        :param return_type: The type the function returns
        :type return_type: type
        :rtype: MethodSignature
        """
        ordered_pairs = [(name, parameter_types[name]) for name in parameter_names]
        return MethodSignature(ordered_pairs, return_type)
