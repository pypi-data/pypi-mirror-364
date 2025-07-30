# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Union

from .common import *
from .diagram import *
from .equations import *
from .expressions import *
from .forward import *
from .globals import *
from .groupdecl import *
from .instances import *
from .modules import *
from .operators import *
from .scopes import *
from .scopesections import *
from .typedecl import *
from .variable import *
from .harness import *
from .pragmas import *


def swan_to_str(swan: Union[SwanItem, None], normalize: bool = False) -> str:  # noqa: F405
    """Convert a SwanItem to a string.
    When normalize is True, the output is normalized to a canonical form.
    """
    import ansys.scadeone.core.svc.swan_printer as swan_printer

    return swan_printer.swan_to_str(swan, normalize)
