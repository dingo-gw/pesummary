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
import glob
import copy

import argparse

from pesummary.gw.inputs import GWInput, GWPostProcessing
from pesummary.core.command_line import command_line
from pesummary.gw.command_line import (
    insert_gwspecific_option_group, add_dynamic_PSD_to_namespace,
    add_dynamic_calibration_to_namespace
)
from .base import make_result_file, gw_parameters, data_dir

import numpy as np
import h5py

import pytest


class TestCommandLine(object):

    def setup(self):
        self.parser = command_line()
        insert_gwspecific_option_group(self.parser)
        if not os.path.isdir(".outdir"):
            os.mkdir(".outdir")
        make_result_file(gw=True, lalinference=True, outdir=".outdir/")
        os.rename(".outdir/test.hdf5", ".outdir/lalinference_example.h5")
        make_result_file(gw=True, bilby=True, outdir=".outdir/", extension="hdf5")
        os.rename(".outdir/test.h5", ".outdir/bilby_example.h5")

    def teardown(self):
        """Remove the files and directories created from this class
        """
        if os.path.isdir(".outdir"):
            shutil.rmtree(".outdir") 

    def test_webdir(self):
        assert self.parser.get_default("webdir") == None
        opts = self.parser.parse_args(["--webdir", "test"])
        assert opts.webdir == "test"

    def test_baseurl(self):
        assert self.parser.get_default("baseurl") == None
        opts = self.parser.parse_args(["--baseurl", "test"])
        assert opts.baseurl == "test"

    def test_add_to_existing(self):
        assert self.parser.get_default("add_to_existing") == False
        opts = self.parser.parse_args(["--add_to_existing"])
        assert opts.add_to_existing == True

    def test_approximant(self):
        assert self.parser.get_default("approximant") == None
        opts = self.parser.parse_args(["--approximant", "test"])
        assert opts.approximant == ["test"]

    def test_config(self):
        assert self.parser.get_default("config") == None
        opts = self.parser.parse_args(["--config", "test"])
        assert opts.config == ["test"]

    def test_dump(self):
        assert self.parser.get_default("dump") == False
        opts = self.parser.parse_args(["--dump"])
        assert opts.dump == True

    def test_email(self):
        assert self.parser.get_default("email") == None
        opts = self.parser.parse_args(["--email", "test"])
        assert opts.email == "test"

    def test_existing(self):
        assert self.parser.get_default("existing") == None
        opts = self.parser.parse_args(["--existing_webdir", "test"])
        assert opts.existing == "test"

    def test_gracedb(self):
        assert self.parser.get_default("gracedb") == None
        opts = self.parser.parse_args(["--gracedb", "Gtest"])
        assert opts.gracedb == "Gtest"

    def test_inj_file(self):
        assert self.parser.get_default("inj_file") == None
        opts = self.parser.parse_args(["--inj_file", "test"])
        assert opts.inj_file == ["test"]

    def test_samples(self):
        assert self.parser.get_default("samples") == None
        opts = self.parser.parse_args(["--samples", "test"])
        assert opts.samples == ["test"]

    def test_sensitivity(self):
        assert self.parser.get_default("sensitivity") == False
        opts = self.parser.parse_args(["--sensitivity"])
        assert opts.sensitivity == True

    def test_user(self):
        assert self.parser.get_default("user") == "albert.einstein"
        opts = self.parser.parse_args(["--user", "test"])
        assert opts.user == "test"

    def test_verbose(self):
        opts = self.parser.parse_args(["-v"])
        assert opts.verbose == True

    def test_gwdata(self):
        opts = self.parser.parse_args(["--gwdata", "H1:H1-CALIB-STRAIN:hello.lcf"])
        assert opts.gwdata == {"H1:H1-CALIB-STRAIN": "hello.lcf"}


class TestInputExceptions(object):

    def setup(self):
        if os.path.isdir("./.outdir"):
            shutil.rmtree("./.outdir")
        os.mkdir('./.outdir')
        self.parser = command_line()
        insert_gwspecific_option_group(self.parser)
        make_result_file(gw=True, lalinference=True, outdir=".outdir/")
        os.rename(".outdir/test.hdf5", ".outdir/lalinference_example.h5")
        make_result_file(gw=True, bilby=True, outdir=".outdir/", extension="hdf5")
        os.rename(".outdir/test.h5", ".outdir/bilby_example.h5")

    def test_no_webdir(self):
        with pytest.raises(Exception) as info:
            opts = self.parser.parse_args([])
            x = GWInput(opts)
        assert "Please provide a web directory" in str(info.value)

    def test_make_webdir_if_it_does_not_exist(self):
        assert os.path.isdir("./.outdir/path") == False
        opts = self.parser.parse_args(['--webdir', './.outdir/path',
                                       '--approximant', 'IMRPhenomPv2',
                                       '--samples', "./.outdir/bilby_example.h5"])
        x = GWInput(opts)
        assert os.path.isdir("./.outdir/path") == True

    def test_invalid_existing_directory(self):
        if os.path.isdir("./.existing"):
            shutil.rmtree("./.existing")
        with pytest.raises(Exception) as info:
            opts = self.parser.parse_args(['--existing_webdir', './.existing'])
            x = GWInput(opts)
        dir_name = os.path.abspath('./.existing')
        assert "Please provide a valid existing directory" in str(info.value)

    def test_not_base_of_existing_directory(self):
        if os.path.isdir("./.existing2"):
            shutil.rmtree("./.existing2")
        if os.path.isdir("./.existing2/samples"):
            shutil.rmtree("./.existing2/samples")
        os.mkdir("./.existing2")
        os.mkdir("./.existing2/samples")
        opts = self.parser.parse_args(['--existing_webdir', './.existing2/samples'])
        with pytest.raises(Exception) as info:
            x = GWInput(opts)
        assert "Please provide a valid existing directory" in str(info.value)

    def test_add_to_existing_and_no_existing_flag(self):
        opts = self.parser.parse_args(["--add_to_existing"])
        with pytest.raises(Exception) as info:
            x = GWInput(opts)
        assert "Please provide a web directory to store the webpages" in str(info.value)

    def test_no_samples(self):
        opts = self.parser.parse_args(["--webdir", "./.outdir"])
        with pytest.raises(Exception) as info:
            x = GWInput(opts)
        assert "Please provide a results file" in str(info.value)

    def test_non_existance_samples(self):
        opts = self.parser.parse_args(["--webdir", "./.outdir",
                                       "--samples", "./.outdir/no_existance"])
        with pytest.raises(Exception) as info:
            x = GWInput(opts)
        assert "File ./.outdir/no_existance does not exist" in str(info.value)

    def test_napproximant_not_equal_to_nsamples(self):
        opts = self.parser.parse_args(["--webdir", "./.outdir",
                                       "--samples", "./.outdir/bilby_example.h5",
                                       "./.outdir/bilby_example.h5",
                                       "--approximant", "IMRPhenomPv2"])
        with pytest.raises(Exception) as info:
            x = GWInput(opts)
        assert "Please pass an approximant for each" in str(info.value)


class TestInput(object):

    def setup(self):
        if not os.path.isdir(".outdir"):
            os.mkdir(".outdir")
        self.parser = command_line()
        insert_gwspecific_option_group(self.parser)
        make_result_file(gw=True, lalinference=True, outdir=".outdir/")
        os.rename(".outdir/test.hdf5", ".outdir/lalinference_example.h5")
        make_result_file(gw=True, bilby=True, outdir=".outdir/", extension="hdf5")
        os.rename(".outdir/test.h5", ".outdir/bilby_example.h5")
        self.default_arguments = [
            "--approximant", "IMRPhenomPv2",
            "--webdir", "./.outdir",
            "--samples", "./.outdir/bilby_example.h5",
            "--email", "albert.einstein@ligo.org",
            "--gracedb", "Grace",
            "--labels", "example"]
        self.original_arguments = copy.deepcopy(self.default_arguments)
        self.make_input_object()

    def teardown(self):
        """Remove the files and directories created from this class
        """
        if os.path.isdir(".outdir"):
            shutil.rmtree(".outdir")

    @staticmethod
    def make_existing_file(path):
        parameters = np.array(["mass_1", "mass_2", "luminosity_distance"],
                              dtype="S")
        samples = np.array([[10, 5, 400], [40, 20, 800], [50, 10, 200]])
        injected_samples = np.array([float("nan"), float("nan"), float("nan")])

        f = h5py.File(path + "/posterior_samples.h5", "w")
        posterior_samples = f.create_group("posterior_samples")
        label = posterior_samples.create_group("example")
        label.create_dataset("parameter_names", data=parameters)
        label.create_dataset("samples", data=samples)
        injection_data = f.create_group("injection_data")
        label = injection_data.create_group("example")
        label.create_dataset("injection_values", data=injected_samples)
        f.close()
        return path + "/posterior_samples.h5"

    def add_argument(self, argument, reset=False):
        if reset:
            self.default_arguments = self.original_arguments
        if isinstance(argument, list):
            for i in argument:
                self.default_arguments.append(i)
        else:
            self.default_arguments.append(argument)
        self.opts, unknown = self.parser.parse_known_args(self.default_arguments)
        add_dynamic_PSD_to_namespace(self.opts)
        add_dynamic_calibration_to_namespace(self.opts)
        self.inputs = GWInput(self.opts)

    def replace_existing_argument(self, argument, new_value):
        if argument in self.default_arguments:
            index = self.default_arguments.index(argument)
            arguments = self.default_arguments
            arguments[index+1] = new_value
            self.default_arguments = arguments
        self.make_input_object()

    def make_input_object(self):
        self.opts, unknown = self.parser.parse_known_args(self.default_arguments)
        add_dynamic_PSD_to_namespace(self.opts)
        add_dynamic_calibration_to_namespace(self.opts)
        self.inputs = GWInput(self.opts)

    def test_webdir(self):
        assert self.inputs.webdir == os.path.abspath("./.outdir")

    def test_samples(self):
        assert self.inputs.result_files == ["./.outdir/bilby_example.h5"]

    def test_approximant(self):
        assert self.inputs.approximant == {"example": "IMRPhenomPv2"}

    def test_existing(self):
        assert self.inputs.existing == None

    def test_baseurl(self):
        assert self.inputs.baseurl == "https://" + os.path.abspath("./.outdir")

    def test_inj_file(self):
        assert self.inputs.injection_file == [None]

    def test_config(self):
        assert self.inputs.config == [None]

    def test_email(self):
        assert self.inputs.email == "albert.einstein@ligo.org"

    def test_add_to_existing(self):
        assert self.inputs.add_to_existing == False

    def test_sensitivity(self):
        assert self.inputs.sensitivity == False

    def test_dump(self):
        assert self.inputs.dump == False
        self.add_argument(["--dump"])
        assert self.inputs.dump == True

    def test_gracedb(self):
        assert self.inputs.gracedb == "Grace"
        parser = command_line()
        insert_gwspecific_option_group(parser)
        default_arguments = [
            "--approximant", "IMRPhenomPv2",
            "--webdir", "./.outdir",
            "--samples", "./.outdir/bilby_example.h5",
            "--email", "albert.einstein@ligo.org",
            "--gracedb", "Mock",
            "--labels", "example"]
        opts = parser.parse_args(default_arguments)
        inputs = GWInput(opts)
        assert inputs.gracedb is None

    def test_detectors(self):
        assert self.inputs.detectors == {"example": None}

    def test_labels(self):
        assert self.inputs.labels == ["example"]
        self.add_argument(["--label", "new_example"])
        assert self.inputs.labels == ["new_example"]

    def test_existing_labels(self):
        assert self.inputs.existing_labels == None
        path = self.make_existing_file("./.outdir/samples")
        with open("./.outdir/home.html", "w") as f:
            f.writelines("test")
        parser = command_line()
        insert_gwspecific_option_group(parser)
        default_arguments = [
            "--approximant", "IMRPhenomPv2",
            "--existing_webdir", "./.outdir",
            "--samples", "./.outdir/bilby_example.h5",
            "--gracedb", "Grace"]
        opts = parser.parse_args(default_arguments)
        inputs = GWInput(opts)
        assert inputs.existing_labels == ["example"]

    def test_existing_samples(self):
        assert self.inputs.existing_samples == None
        path = self.make_existing_file("./.outdir/samples")
        with open("./.outdir/home.html", "w") as f:
            f.writelines("test")
        parser = command_line()
        insert_gwspecific_option_group(parser)
        default_arguments = [
            "--approximant", "IMRPhenomPv2",
            "--existing_webdir", "./.outdir",
            "--samples", "./.outdir/bilby_example.h5",
            "--email", "albert.einstein@ligo.org",
            "--gracedb", "Grace"]
        opts = parser.parse_args(default_arguments)
        inputs = GWInput(opts)
        assert all(
            i == j for i, j in zip(inputs.existing_samples["example"]["mass_1"], [10, 40, 50]))
        assert all(
            i == j for i,j in zip(inputs.existing_samples["example"]["mass_2"], [5, 20, 10]))
        assert all(
            i == j for i,j in zip(inputs.existing_samples["example"]["luminosity_distance"], [400, 800, 200]))

    def test_psd(self):
        with open("./.outdir/psd.dat", "w") as f:
            f.writelines(["1.00 3.44\n", "2.00 5.66\n", "3.00 4.56\n", "4.00 9.83\n"])
        assert self.inputs.psd == {"example": {}}
        self.add_argument(["--psd", "./.outdir/psd.dat"])
        assert list(self.inputs.psd["example"].keys()) == ["psd.dat"]
        self.add_argument(["--psd", "H1:./.outdir/psd.dat"])
        assert list(self.inputs.psd["example"].keys()) == ["H1"]
        np.testing.assert_almost_equal(
            self.inputs.psd["example"]["H1"],
            [[1.00, 3.44], [2.00, 5.66], [3.00, 4.56], [4.00, 9.83]]
        )

    def test_preliminary_pages_for_single_analysis(self):
        """Test that preliminary watermarks are added when an analysis
        is not reproducible
        """
        # when neither a psd or config is passed, add preliminary watermark
        assert self.inputs.preliminary_pages == {"example": True}
        # when a psd is added but not a config, add preliminary watermark
        with open("./.outdir/psd.dat", "w") as f:
            f.writelines(["1.00 3.44\n", "2.00 5.66\n", "3.00 4.56\n", "4.00 9.83\n"])
        self.add_argument(["--psd", "./.outdir/psd.dat"])
        assert self.inputs.preliminary_pages == {"example": True}
        # when a config is added but no psd, add preliminary watermark
        self.add_argument(
            ["--config", data_dir + "/config_lalinference.ini"], reset=True
        )
        assert self.inputs.preliminary_pages == {"example": True}
        # when both config and psd is added, do not add preliminary watermark
        self.add_argument(
            ["--psd", "./.outdir/psd.dat"], reset=True
        )
        self.add_argument(["--config", data_dir + "/config_lalinference.ini"])
        assert self.inputs.preliminary_pages == {"example": False}

    def test_preliminary_pages_for_multiple_analysis(self):
        """Test that preliminary watermarks are added when multiple analyses
        are not reproducible
        """
        with open("./.outdir/psd.dat", "w") as f:
            f.writelines(["1.00 3.44\n", "2.00 5.66\n", "3.00 4.56\n", "4.00 9.83\n"])
        self.default_arguments = [
            "--approximant", "IMRPhenomPv2", "IMRPhenomPv2",
            "--webdir", "./.outdir",
            "--samples", "./.outdir/bilby_example.h5", "./.outdir/bilby_example.h5",
            "--email", "albert.einstein@ligo.org",
            "--gracedb", "Grace",
            "--labels", "example", "example2"]
        self.original_arguments = copy.deepcopy(self.default_arguments)
        self.make_input_object()
        # when neither a psd or config is passed for each file, add preliminary
        # watermark
        assert self.inputs.preliminary_pages["example"] == True
        assert self.inputs.preliminary_pages["example2"] == True
        # When a psd and config is provided to both analyses, add preliminary
        # watermark to both files
        self.add_argument(["--psd", "H1:./.outdir/psd.dat"])
        self.add_argument(
            ["--config", data_dir + "/config_lalinference.ini",
             data_dir + "/config_lalinference.ini"]
        )
        assert self.inputs.preliminary_pages["example"] == False
        assert self.inputs.preliminary_pages["example2"] == False

    def test_calibration(self):
        with open("./.outdir/calibration.dat", "w") as f:
            f.writelines(["1.0 2.0 3.0 4.0 5.0 6.0 7.0\n"])
            f.writelines(["1.0 2.0 3.0 4.0 5.0 6.0 7.0"])
        assert self.inputs.calibration == {"example": {None: None}}
        self.add_argument(["--calibration", "./.outdir/calibration.dat"])
        assert self.inputs.calibration["example"] == {None: None}
        assert list(self.inputs.priors["calibration"]["example"].keys()) == ['calibration.dat']

    def test_custom_psd(self):
        with open("./.outdir/psd.dat", "w") as f:
            f.writelines(["1.00 3.44\n", "2.00 5.66\n", "3.00 4.56\n", "4.00 9.83\n"])
        parser = command_line()
        insert_gwspecific_option_group(parser)
        default_arguments = [
            "--approximant", "IMRPhenomPv2", "IMRPhenomPv2",
            "--webdir", "./.outdir",
            "--samples", "./.outdir/bilby_example.h5",
            "./.outdir/bilby_example.h5",
            "--email", "albert.einstein@ligo.org",
            "--gracedb", "Grace",
            "--labels", "test", "test2",
            "--test_psd", "L1:./.outdir/psd.dat",
            "--test2_psd", "V1:./.outdir/psd.dat",
            "--gw"
        ]
        opts, unknown = parser.parse_known_args(default_arguments)
        add_dynamic_PSD_to_namespace(opts, command_line=default_arguments)
        add_dynamic_calibration_to_namespace(
            opts, command_line=default_arguments
        )
        inputs = GWInput(opts)
        assert sorted(list(inputs.psd.keys())) == sorted(["test", "test2"])
        assert list(inputs.psd["test"].keys()) == ["L1"]
        assert list(inputs.psd["test2"].keys()) == ["V1"]
        np.testing.assert_almost_equal(
            inputs.psd["test"]["L1"],
            [[1.00, 3.44], [2.00, 5.66], [3.00, 4.56], [4.00, 9.83]]
        )

    def test_IFO_from_file_name(self):
        file_name = "IFO0.dat"
        assert GWInput.get_ifo_from_file_name(file_name) == "H1"
        file_name = "IFO1.dat"
        assert GWInput.get_ifo_from_file_name(file_name) == "L1"
        file_name = "IFO2.dat"
        assert GWInput.get_ifo_from_file_name(file_name) == "V1"

        file_name = "IFO_H1.dat"
        assert GWInput.get_ifo_from_file_name(file_name) == "H1"
        file_name = "IFO_L1.dat"
        assert GWInput.get_ifo_from_file_name(file_name) == "L1"
        file_name = "IFO_V1.dat"
        assert GWInput.get_ifo_from_file_name(file_name) == "V1"
        
        file_name = "example.dat"
        assert GWInput.get_ifo_from_file_name(file_name) == "example.dat"

    def test_ignore_parameters(self):
        parser = command_line()
        insert_gwspecific_option_group(parser)
        default_arguments = [
            "--approximant", "IMRPhenomPv2",
            "--webdir", "./.outdir",
            "--samples", "./.outdir/bilby_example.h5",
            "--labels", "example"]
        opts = parser.parse_args(default_arguments)
        original = GWInput(opts)

        parser = command_line()
        insert_gwspecific_option_group(parser)
        default_arguments = [
            "--approximant", "IMRPhenomPv2",
            "--webdir", "./.outdir",
            "--samples", "./.outdir/bilby_example.h5",
            "--ignore_parameters", "cos*",
            "--labels", "example"]
        opts = parser.parse_args(default_arguments)
        ignored = GWInput(opts)
        ignored_params = [
            param for param in list(original.samples["example"].keys()) if
            "cos" in param
        ]
        assert all(
            param not in list(ignored.samples["example"].keys()) for param in
            ignored_params
        )
        for param, samples in ignored.samples["example"].items():
            np.testing.assert_almost_equal(
                samples, original.samples["example"][param]
            )

    def test_make_directories(self):
        assert os.path.isdir("./.outdir/samples/samples") == False
        self.replace_existing_argument("--webdir", "./.outdir/samples")
        self.inputs.make_directories()
        assert os.path.isdir("./.outdir/samples/samples") == True

    def test_copy_files(self):
        if os.path.isdir("./.outdir/samples"):
            shutil.rmtree("./.outdir/samples")
        assert os.path.isfile(
            "./.outdir/samples/js/combine_corner.js") == False
        self.replace_existing_argument("--webdir", "./.outdir/samples")
        self.add_argument(["--config", data_dir + "/config_lalinference.ini"])
        self.inputs.copy_files()
        assert os.path.isfile(
            "./.outdir/samples/js/combine_corner.js") == True
        assert os.path.isfile(
            "./.outdir/samples/config/example_config.ini") == True


class TestPostProcessing(object):

    def setup(self):
        if not os.path.isdir(".outdir"):
            os.mkdir(".outdir")
        self.parser = command_line()
        insert_gwspecific_option_group(self.parser)
        make_result_file(gw=True, lalinference=True, outdir=".outdir/")
        os.rename(".outdir/test.hdf5", ".outdir/lalinference_example.h5")
        data = make_result_file(gw=True, bilby=True, outdir=".outdir/", extension="hdf5")
        self.parameters, self.samples = data
        os.rename(".outdir/test.h5", ".outdir/bilby_example.h5")
        self.opts = self.parser.parse_args(["--approximant", "IMRPhenomPv2",
            "--webdir", "./.outdir", "--samples", "./.outdir/bilby_example.h5",
            "--email", "albert.einstein@ligo.org", "--gracedb", "Grace",
            "--labels", "example"])
        self.inputs = GWInput(self.opts)
        self.postprocessing = GWPostProcessing(self.inputs)

    def teardown(self):
        """Remove the files and directories created from this class
        """
        if os.path.isdir(".outdir"):
            shutil.rmtree(".outdir")

    def test_injection_data(self):
        assert sorted(list(self.postprocessing.injection_data["example"].keys())) == sorted(
            gw_parameters())

    def test_maxL_samples(self):
        ind = self.parameters.index("log_likelihood")
        likelihood = np.array(self.samples).T[ind]
        max_ind = np.argmax(likelihood)
        for param in self.parameters:
            ind = self.parameters.index(param)
            assert self.postprocessing.maxL_samples["example"][param] == self.samples.T[ind][max_ind]
        assert self.postprocessing.maxL_samples["example"]["approximant"] == "IMRPhenomPv2"

    def test_same_parameters(self):
        parser = command_line()
        insert_gwspecific_option_group(parser)
        opts = parser.parse_args(["--approximant", "IMRPhenomPv2",
            "IMRPhenomPv2", "--webdir", "./.outdir", "--samples",
            "./.outdir/bilby_example.h5", "./.outdir/lalinference_example.h5"])
        inputs = GWInput(opts)
        postprocessing = GWPostProcessing(inputs)
        assert sorted(postprocessing.same_parameters) == sorted(gw_parameters())

    def test_psd_labels(self):
        assert list(self.postprocessing.psd.keys()) == ["example"]
        assert self.postprocessing.psd["example"] == {}
        with open("./.outdir/psd.dat", "w") as f:
            f.writelines(["1.00 3.44\n", "2.00 5.66\n", "3.00 4.56\n", "4.00 9.83\n"])
        parser = command_line()
        insert_gwspecific_option_group(parser)
        opts = parser.parse_args(["--approximant", "IMRPhenomPv2",
            "IMRPhenomPv2", "--webdir", "./.outdir", "--samples",
            "./.outdir/bilby_example.h5", "./.outdir/lalinference_example.h5",
            "--psd", "L1:./.outdir/psd.dat", "L1:./.outdir/psd.dat",
            "--labels", "example", "example2"])
        inputs = GWInput(opts)
        postprocessing = GWPostProcessing(inputs)
        assert sorted(list(postprocessing.psd["example"].keys())) == ["L1"]
        assert sorted(list(postprocessing.psd["example2"].keys())) == ["L1"]
