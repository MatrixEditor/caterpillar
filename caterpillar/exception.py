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


class StructException(Exception):
    """Base class for all struct-related exceptions"""


class DynamicSizeError(StructException):
    """
    Exception raised for errors related to dynamic sizes in structs.

    This can be used when there are issues with determining the size of a struct element at runtime.
    """


class OptionError(StructException):
    """
    Exception raised for errors related to options in structs.

    This can be used when there are issues with handling options or choices within a struct.
    """


class ValidationError(StructException):
    """
    Exception raised for errors related to validation in structs.

    This can be used when there are issues with validating the structure or content of a struct.
    """


class UnsupportedOperation(StructException):
    """
    Exception raised for unsupported operations in structs.

    This can be used when attempting an operation that is not supported or allowed in the context of structs.
    """
