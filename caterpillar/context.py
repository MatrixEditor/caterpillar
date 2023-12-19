# Copyright (C) MatrixEditor 2023
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from __future__ import annotations

from caterpillar.abc import _ContextLambda, _ContextLike


class Context(_ContextLike):
    """Represents a context object with attribute-style access."""

    def __setattr__(self, key: str, value) -> None:
        """
        Sets an attribute in the context.

        :param key: The attribute key.
        :param value: The value to be set.
        """
        self[key] = value

    def __getattribute__(self, key: str):
        """
        Retrieves an attribute from the context.

        :param key: The attribute key.
        :return: The value associated with the key.
        """
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            if "." not in key:
                return self[key]  # Raises an error if the key is not found

            path = key.split(".")
            root = self[path[0]]
            for i in range(1, len(path)):
                root = getattr(root, path[i])

            return root


# TODO: insert ExprMixin to support operations
class ContextPath(_ContextLambda):
    """
    Represents a lambda function for retrieving a value from a Context based on a specified path.
    """

    def __init__(self, path: str = None) -> None:
        """
        Initializes a ContextPath instance with an optional path.

        :param path: The path to use when retrieving a value from a Context.
        """
        self.path = path

    def __call__(self, context: Context, **kwds):
        """
        Calls the lambda function to retrieve a value from a Context.

        :param context: The Context from which to retrieve the value.
        :param kwds: Additional keyword arguments (ignored in this implementation).
        :return: The value retrieved from the Context based on the path.
        """
        return getattr(context, self.path)

    def __getattribute__(self, key: str) -> ContextPath:
        """
        Gets an attribute from the ContextPath, creating a new instance if needed.

        :param key: The attribute key.
        :return: A new ContextPath instance with an updated path.
        """
        try:
            return super().__getattribute__(key)
        except AttributeError:
            if not self.path:
                return ContextPath(key)
            return ContextPath(".".join([self.path, key]))

    def __repr__(self) -> str:
        """
        Returns a string representation of the ContextPath.

        :return: A string representation.
        """
        return f"<Path {self.path!r}>"

    def __str__(self) -> str:
        """
        Returns a string representation of the path.

        :return: A string representation of the path.
        """
        return self.path
