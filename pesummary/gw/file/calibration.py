# Copyright (C) 2020  Charlie Hoy <charlie.hoy@ligo.org>
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import numpy as np
from pesummary import conf


class Calibration(np.ndarray):
    """Class to handle Calibration data
    """
    def __new__(cls, input_array):
        obj = np.asarray(input_array).view(cls)
        if obj.shape[1] != 7:
            raise ValueError(
                "Invalid input data. See the docs for instructions"
            )
        return obj

    def save_to_file(self, file_name):
        """Save the calibration data to file

        Parameters
        ----------
        file_name: str
            name of the file name that you wish to use
        """
        if os.path.isfile(file_name):
            raise FileExistsError("File already exists")
        header = [
            "Frequency", "Median Mag", "Phase (Rad)", "-1 Sigma Mag",
            "-1 Sigma Phase", "+1 Sigma Mag", "+1 Sigma Phase"
        ]
        np.savetxt(
            file_name, self, delimiter=conf.delimiter,
            header=conf.delimiter.join(header), comments=""
        )

    def __array_finalize__(self, obj):
        if obj is None:
            return
