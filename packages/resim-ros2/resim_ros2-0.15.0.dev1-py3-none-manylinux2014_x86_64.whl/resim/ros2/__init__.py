# Copyright 2023 ReSim, Inc.
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

import os
import pathlib

RESIM_DIR = pathlib.Path(__file__).parent.parent.resolve()
LIB_DIR = pathlib.Path(__file__).parent.parent.parent.resolve() / "resim.libs"
os.environ["AMENT_PREFIX_PATH"] = str(LIB_DIR / "ament")
os.environ["RMW_IMPLEMENTATION"] = str(LIB_DIR / "librmw_cyclonedds.so")
