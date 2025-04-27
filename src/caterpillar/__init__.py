# Copyright (C) MatrixEditor 2023-2025
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
import warnings

__version__ = "2.4.4"
__release__ = None
__author__ = "MatrixEditor"


def native_support():
    """Return True if native support is available."""
    try:
        # pylint: disable-next=import-outside-toplevel
        from caterpillar import _C

        return True
    except ImportError:
        return False


# Explicitly report deprecation warnings
warnings.filterwarnings("default", module="caterpillar")