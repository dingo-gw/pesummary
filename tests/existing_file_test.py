# Copyright (C) 2018  Charlie Hoy <charlie.hoy@ligo.org>
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
import shutil

from pesummary.gw.file.existing import GWExistingFile

import h5py
import numpy as np
import pytest


class TestExistingFile(object):

    def setup(self):
        self.existing = "./.outdir_existing"
        if os.path.isdir(self.existing):
            shutil.rmtree(self.existing)
        os.makedirs(self.existing)
        os.makedirs(self.existing + "/samples")

        parameters = np.array(["mass_1", "mass_2"], dtype="S")
        samples = np.array([[2.0, 1.0], [4.0, 2.0]])
        injection_values = np.array([1.0, 2.0])
        f = h5py.File("./.outdir_existing/samples/posterior_samples.h5")
        posterior_samples = f.create_group("posterior_samples")
        label = posterior_samples.create_group("label")
        label.create_dataset("parameter_names", data=parameters)
        label.create_dataset("samples", data=samples)
        injection_data = f.create_group("injection_data")
        label = injection_data.create_group("label")
        label.create_dataset("injection_values", data=injection_values)
        f.close()

        self.existing_object = GWExistingFile(self.existing)

    def test_existing_file(self):
        assert self.existing_object.existing_file == (
            "./.outdir_existing/samples/posterior_samples.h5")

    def test_existing_labels(self):
        assert self.existing_object.existing_labels == ["label"]

    def test_existing_samples(self):
        assert all(
            i == j for i,j in zip(
                self.existing_object.existing_samples[0][0], np.array([2., 1.])))
        assert all(
            i == j for i,j in zip(
                self.existing_object.existing_samples[0][1], np.array([4., 2.])))

    def test_existing_parameters(self):
        assert all(
            i == j for i,j in zip(
                self.existing_object.existing_parameters[0], ["mass_1", "mass_2"]))

    def test_existing_injection(self):
        assert all(
            i == j for i,j in zip(
                self.existing_object.existing_injection[0], [1.0, 2.0]))
