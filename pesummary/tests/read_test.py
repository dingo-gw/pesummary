import os
import shutil
import numpy as np

from .base import make_result_file
import pesummary
from pesummary.gw.file.read import read as GWRead
from pesummary.core.file.read import read as Read


class BaseRead(object):
    """Base class to test the core functions in the Read and GWRead functions
    """
    def test_parameters(self, true, pesummary=False):
        """Test the parameter property
        """
        if pesummary:
            assert all(i in self.result.parameters[0] for i in true)
            assert all(i in true for i in self.result.parameters[0])
        else:
            assert all(i in self.result.parameters for i in true)
            assert all(i in true for i in self.result.parameters)

    def test_samples(self, true, pesummary=False):
        """Test the samples property
        """
        if pesummary:
            assert len(self.result.samples[0]) == 1000
            assert len(self.result.samples[0][0]) == 18
            true_flat = [item for sublist in true for item in sublist]
            flat = [item for sublist in self.result.samples[0] for item in sublist]
            assert all(i in true_flat for i in flat)
            assert all(i in flat for i in true_flat)
        else:
            assert len(self.result.samples) == 1000
            assert len(self.result.samples[0]) == 18
            true_flat = [item for sublist in true for item in sublist]
            flat = [item for sublist in self.result.samples for item in sublist]
            assert all(i in true_flat for i in flat)
            assert all(i in flat for i in true_flat)

    def test_samples_dict(self, true):
        """Test the samples_dict property
        """
        parameters = true[0]
        samples = true[1]
        for num, param in enumerate(parameters):
            specific_samples = [i[num] for i in samples]
            drawn_samples = self.result.samples_dict[param]
            assert all(i == j for i, j in zip(drawn_samples, specific_samples))

    def test_version(self, true=None):
        """Test the version property
        """
        if true is None:
            assert self.result.input_version == "No version information found"
        else:
            assert self.result.input_version == true

    def test_extra_kwargs(self, true=None):
        """Test the extra_kwargs property
        """
        if true is None:
            assert self.result.extra_kwargs == {"sampler": {"nsamples": 1000}, "meta_data": {}}
        else:
            assert sorted(self.result.extra_kwargs) == sorted(true)

    def test_injection_parameters(self, true, pesummary=False):
        """Test the injection_parameters property
        """
        if true is None:
            assert self.result.injection_parameters is None
        else:
            import math

            assert all(i in list(true.keys()) for i in self.parameters)
            assert all(i in self.parameters for i in list(true.keys()))

            if not pesummary:
                for i in true.keys():
                    if math.isnan(true[i]):
                        assert math.isnan(self.result.injection_parameters[i])
                    else:
                        assert true[i] == self.result.injection_parameters[i]

    def test_to_dat(self):
        """Test the to_dat method
        """
        self.result.to_dat(outdir=".outdir", label="label")
        assert os.path.isfile(os.path.join(".outdir", "pesummary_label.dat"))
        data = np.genfromtxt(
            os.path.join(".outdir", "pesummary_label.dat"), names=True)
        assert all(i in self.parameters for i in list(data.dtype.names))
        assert all(i in list(data.dtype.names) for i in self.parameters)
        for param in self.parameters:
            assert np.testing.assert_almost_equal(
                data[param], self.result.samples_dict[param], 8
            ) is None

    def test_file_format_read(self, path, file_format, _class, function=Read):
        """Test that when the file_format is specified, that correct class is used
        """
        result = function(path, file_format=file_format)
        assert isinstance(result, _class)

    def test_downsample(self):
        """Test the .downsample method. This includes testing that the
        .downsample method downsamples to the specified number of samples,
        that it only takes samples that are currently in the posterior
        table and that it maintains concurrent samples.
        """
        old_samples_dict = self.result.samples_dict
        nsamples = 50
        self.result.downsample(nsamples)
        assert self.result.samples_dict.number_of_samples == nsamples
        for param in self.parameters:
            assert all(
                samp in old_samples_dict[param] for samp in
                self.result.samples_dict[param]
            )
        for num in range(nsamples):
            samp_inds = [
                old_samples_dict[param].tolist().index(
                    self.result.samples_dict[param][num]
                ) for param in self.parameters
            ]
            assert len(set(samp_inds)) == 1


class GWBaseRead(BaseRead):
    """Base class to test the GWRead specific functions
    """
    def test_parameters(self, true, pesummary=False):
        """Test the parameter property
        """
        super(GWBaseRead, self).test_parameters(true, pesummary=pesummary)
        from .base import gw_parameters
        full_parameters = gw_parameters()

        self.result.generate_all_posterior_samples()
        assert all(i in self.result.parameters for i in full_parameters)
        assert all(i in full_parameters for i in self.result.parameters)

    def test_injection_parameters(self, true):
        """Test the injection_parameters property
        """
        import math

        super(GWBaseRead, self).test_injection_parameters(true)
        self.result.add_injection_parameters_from_file("./tests/main_injection.xml", conversion=False)
        true = {
            'dec': [1.949725], 'geocent_time': [1186741861], 'spin_2x': [0.],
            'spin_2y': [0.], 'spin_2z': [0.], 'luminosity_distance': [139.7643],
            'ra': [-1.261573], 'spin_1y': [0.], 'spin_1x': [0.], 'spin_1z': [0.],
            'psi': [1.75], 'phase': [0.], 'iota': [1.0471976],
            'mass_1': [53.333332], 'mass_2': [26.666668],
            'symmetric_mass_ratio': [0.22222222], 'a_1': float('nan'),
            'a_2': float('nan'), 'tilt_1': float('nan'), 'tilt_2': float('nan'),
            'phi_jl': float('nan'), 'phi_12': float('nan'),
            'theta_jn': float('nan'), 'redshift': float('nan'),
            'mass_1_source': float('nan'), 'mass_2_source': float('nan'),
            'log_likelihood': float('nan')
        }
        assert all(i in list(true.keys()) for i in self.parameters)
        for i in true.keys():
            if not isinstance(true[i], list) and math.isnan(true[i]):
                assert math.isnan(self.result.injection_parameters[i])
            else:
                np.testing.assert_almost_equal(
                    true[i], self.result.injection_parameters[i], 5
                )

    def test_calibration_data_in_results_file(self):
        """Test the calibration_data_in_results_file property
        """
        pass

    def test_add_injection_parameters_from_file(self):
        """Test the add_injection_parameters_from_file method
        """
        pass

    def test_add_fixed_parameters_from_config_file(self):
        """Test the add_fixed_parameters_from_config_file method
        """
        pass

    def test_to_lalinference_dat(self):
        """Test the to_lalinference dat=True method
        """
        from pesummary.gw.file.standard_names import lalinference_map

        self.result.to_lalinference(dat=True, outdir=".outdir",
                                    filename="lalinference_label.dat")
        assert os.path.isfile(os.path.join(".outdir", "lalinference_label.dat"))
        data = np.genfromtxt(
            os.path.join(".outdir", "lalinference_label.dat"), names=True)
        for param in data.dtype.names:
            if param not in self.result.parameters:
                pesummary_param = lalinference_map[param]
            else:
                pesummary_param = param
            assert np.testing.assert_almost_equal(
                data[param], self.result.samples_dict[pesummary_param], 8
            ) is None

    def test_file_format_read(self, path, file_format, _class):
        """Test that when the file_format is specified, that correct class is used
        """
        super(GWBaseRead, self).test_file_format_read(
            path, file_format, _class, function=GWRead
        )


class TestCoreJsonFile(BaseRead):
    """Class to test loading in a JSON file with the core Read function
    """
    def setup(self):
        """Setup the TestCoreJsonFile class
        """
        if not os.path.isdir(".outdir"):
            os.mkdir(".outdir")
        self.parameters, self.samples = make_result_file(extension="json", gw=False)
        self.path = os.path.join(".outdir", "test.json")
        self.result = Read(self.path)

    def teardown(self):
        """Remove all files and directories created from this class
        """
        if os.path.isdir(".outdir"):
            shutil.rmtree(".outdir")

    def test_class_name(self):
        """Test the class used to load in this file
        """
        assert isinstance(self.result, pesummary.core.file.formats.default.Default)

    def test_parameters(self):
        """Test the parameter property of the default class
        """
        super(TestCoreJsonFile, self).test_parameters(self.parameters)

    def test_samples(self):
        """Test the samples property of the default class
        """
        super(TestCoreJsonFile, self).test_samples(self.samples)

    def test_samples_dict(self):
        true = [self.parameters, self.samples]
        super(TestCoreJsonFile, self).test_samples_dict(true)

    def test_version(self):
        """Test the version property of the default class
        """
        super(TestCoreJsonFile, self).test_version()

    def test_extra_kwargs(self):
        """Test the extra_kwargs property of the default class
        """
        super(TestCoreJsonFile, self).test_extra_kwargs()

    def test_injection_parameters(self):
        """Test the injection_parameters property
        """
        true = {par: float("nan") for par in self.parameters}
        super(TestCoreJsonFile, self).test_injection_parameters(true)

    def test_to_dat(self):
        """Test the to_dat method
        """
        super(TestCoreJsonFile, self).test_to_dat()

    def test_file_format_read(self):
        """Test that when the file_format is specified, that correct class is used
        """
        from pesummary.core.file.formats.default import Default

        super(TestCoreJsonFile, self).test_file_format_read(self.path, "json", Default)

    def test_downsample(self):
        """Test that the posterior table is correctly downsampled
        """
        super(TestCoreJsonFile, self).test_downsample()


class TestCoreHDF5File(BaseRead):
    """Class to test loading in an HDF5 file with the core Read function
    """
    def setup(self):
        """Setup the TestCoreHDF5File class
        """
        if not os.path.isdir(".outdir"):
            os.mkdir(".outdir")
        self.parameters, self.samples = make_result_file(extension="hdf5", gw=False)
        self.path = os.path.join(".outdir", "test.h5")
        self.result = Read(self.path)

    def teardown(self):
        """Remove the files and directories created from this class
        """
        if os.path.isdir(".outdir"):
            shutil.rmtree(".outdir")

    def test_class_name(self):
        """Test the class used to load in this file
        """
        assert isinstance(self.result, pesummary.core.file.formats.default.Default)

    def test_parameters(self):
        """Test the parameter property of the default class
        """
        super(TestCoreHDF5File, self).test_parameters(self.parameters)

    def test_samples(self):
        """Test the samples property of the default class
        """
        super(TestCoreHDF5File, self).test_samples(self.samples)

    def test_samples_dict(self):
        """Test the samples_dict property of the default class
        """
        true = [self.parameters, self.samples]
        super(TestCoreHDF5File, self).test_samples_dict(true)

    def test_version(self):
        """Test the version property of the default class
        """
        super(TestCoreHDF5File, self).test_version()

    def test_extra_kwargs(self):
        """Test the extra_kwargs property of the default class
        """
        super(TestCoreHDF5File, self).test_extra_kwargs()

    def test_injection_parameters(self):
        """Test the injection_parameters property
        """
        true = {par: float("nan") for par in self.parameters}
        super(TestCoreHDF5File, self).test_injection_parameters(true)

    def test_to_dat(self):
        """Test the to_dat method
        """
        super(TestCoreHDF5File, self).test_to_dat()

    def test_file_format_read(self):
        """Test that when the file_format is specified, that correct class is used
        """
        from pesummary.core.file.formats.default import Default

        super(TestCoreHDF5File, self).test_file_format_read(self.path, "hdf5", Default)

    def test_downsample(self):
        """Test that the posterior table is correctly downsampled
        """
        super(TestCoreHDF5File, self).test_downsample()


class TestCoreDatFile(BaseRead):
    """Class to test loading in an dat file with the core Read function
    """
    def setup(self):
        """Setup the TestCoreDatFile class
        """
        if not os.path.isdir(".outdir"):
            os.mkdir(".outdir")
        self.parameters, self.samples = make_result_file(extension="dat", gw=False)
        self.path = os.path.join(".outdir", "test.dat")
        self.result = Read(self.path)

    def teardown(self):
        """Remove the files and directories created from this class
        """
        if os.path.isdir(".outdir"):
            shutil.rmtree(".outdir")

    def test_class_name(self):
        """Test the class used to load in this file
        """
        assert isinstance(self.result, pesummary.core.file.formats.default.Default)

    def test_parameters(self):
        """Test the parameter property of the default class
        """
        super(TestCoreDatFile, self).test_parameters(self.parameters)

    def test_samples(self):
        """Test the samples property of the default class
        """
        super(TestCoreDatFile, self).test_samples(self.samples)

    def test_samples_dict(self):
        """Test the samples_dict property of the default class
        """
        true = [self.parameters, self.samples]
        super(TestCoreDatFile, self).test_samples_dict(true)

    def test_version(self):
        """Test the version property of the default class
        """
        super(TestCoreDatFile, self).test_version()

    def test_extra_kwargs(self):
        """Test the extra_kwargs property of the default class
        """
        super(TestCoreDatFile, self).test_extra_kwargs()

    def test_injection_parameters(self):
        """Test the injection_parameters property
        """
        true = {par: float("nan") for par in self.parameters}
        super(TestCoreDatFile, self).test_injection_parameters(true)

    def test_to_dat(self):
        """Test the to_dat method
        """
        super(TestCoreDatFile, self).test_to_dat()

    def test_file_format_read(self):
        """Test that when the file_format is specified, that correct class is used
        """
        from pesummary.core.file.formats.default import Default

        super(TestCoreDatFile, self).test_file_format_read(self.path, "dat", Default)

    def test_downsample(self):
        """Test that the posterior table is correctly downsampled
        """
        super(TestCoreDatFile, self).test_downsample()


class BilbyFile(BaseRead):
    """Base class to test loading in a bilby file with the core Read function
    """
    def test_class_name(self):
        """Test the class used to load in this file
        """
        assert isinstance(self.result, pesummary.core.file.formats.bilby.Bilby)

    def test_parameters(self):
        """Test the parameter property of the bilby class
        """
        super(BilbyFile, self).test_parameters(self.parameters)

    def test_samples(self):
        """Test the samples property of the bilby class
        """
        super(BilbyFile, self).test_samples(self.samples)

    def test_samples_dict(self):
        """Test the samples_dict property of the bilby class
        """
        true = [self.parameters, self.samples]
        super(BilbyFile, self).test_samples_dict(true)

    def test_version(self):
        """Test the version property of the bilby class
        """
        true = "bilby=0.5.3:"
        super(BilbyFile, self).test_version(true)

    def test_extra_kwargs(self):
        """Test the extra_kwargs property of the default class
        """
        true = {"sampler": {
            "log_bayes_factor": 0.5,
            "log_noise_evidence": 0.1,
            "log_evidence": 0.2,
            "log_evidence_err": 0.1},
            "meta_data": {'time_marginalization': True}}
        super(BilbyFile, self).test_extra_kwargs(true)

    def test_injection_parameters(self, true):
        """Test the injection_parameters property
        """
        super(BilbyFile, self).test_injection_parameters(true)

    def test_file_format_read(self, path, file_format):
        """Test that when the file_format is specified, that correct class is used
        """
        from pesummary.core.file.formats.bilby import Bilby

        super(BilbyFile, self).test_file_format_read(path, file_format, Bilby)

    def test_priors(self, read_function=Read):
        """Test that the priors are correctly extracted from the bilby result
        file
        """
        for param, prior in self.result.priors["samples"].items():
            assert isinstance(prior, np.ndarray)
        f = read_function(self.path, disable_prior=True)
        assert not hasattr(f, "priors")
        


class TestCoreJsonBilbyFile(BilbyFile):
    """Class to test loading in a bilby json file with the core Read function
    """
    def setup(self):
        """Setup the TestCoreBilbyFile class
        """
        if not os.path.isdir(".outdir"):
            os.mkdir(".outdir")
        self.parameters, self.samples = make_result_file(
            extension="json", gw=False, bilby=True)
        self.path = os.path.join(".outdir", "test.json")
        self.result = Read(self.path)

    def teardown(self):
        """Remove the files and directories created from this class
        """
        if os.path.isdir(".outdir"):
            shutil.rmtree(".outdir")

    def test_class_name(self):
        """Test the class used to load in this file
        """
        super(TestCoreJsonBilbyFile, self).test_class_name()

    def test_parameters(self):
        """Test the parameter property of the bilby class
        """
        super(TestCoreJsonBilbyFile, self).test_parameters()

    def test_samples(self):
        """Test the samples property of the bilby class
        """
        super(TestCoreJsonBilbyFile, self).test_samples()

    def test_samples_dict(self):
        """Test the samples_dict property of the bilby class
        """
        super(TestCoreJsonBilbyFile, self).test_samples_dict()

    def test_version(self):
        """Test the version property of the default class
        """
        super(TestCoreJsonBilbyFile, self).test_version()

    def test_extra_kwargs(self):
        """Test the extra_kwargs property of the default class
        """
        super(TestCoreJsonBilbyFile, self).test_extra_kwargs()

    def test_injection_parameters(self):
        """Test the injection_parameters property
        """
        true = {par: 1. for par in self.parameters}
        super(TestCoreJsonBilbyFile, self).test_injection_parameters(true)

    def test_to_dat(self):
        """Test the to_dat method
        """
        super(TestCoreJsonBilbyFile, self).test_to_dat()

    def test_file_format_read(self):
        """Test that when the file_format is specified, that correct class is used
        """
        super(TestCoreJsonBilbyFile, self).test_file_format_read(self.path, "bilby")

    def test_downsample(self):
        """Test that the posterior table is correctly downsampled
        """
        super(TestCoreJsonBilbyFile, self).test_downsample()

    def test_priors(self):
        """Test that the priors are correctly extracted from the bilby result
        file
        """
        super(TestCoreJsonBilbyFile, self).test_priors()



class TestCoreHDF5BilbyFile(BilbyFile):
    """Class to test loading in a bilby hdf5 file with the core Read function
    """
    def setup(self):
        """Setup the TestCoreBilbyFile class
        """
        if not os.path.isdir(".outdir"):
            os.mkdir(".outdir")
        self.parameters, self.samples = make_result_file(
            extension="hdf5", gw=False, bilby=True)
        self.path = os.path.join(".outdir", "test.h5")
        self.result = Read(self.path)

    def teardown(self):
        """Remove the files and directories created from this class
        """
        if os.path.isdir(".outdir"):
            shutil.rmtree(".outdir")

    def test_class_name(self):
        """Test the class used to load in this file
        """
        super(TestCoreHDF5BilbyFile, self).test_class_name()

    def test_parameters(self):
        """Test the parameter property of the bilby class
        """
        super(TestCoreHDF5BilbyFile, self).test_parameters()

    def test_samples(self):
        """Test the samples property of the bilby class
        """
        super(TestCoreHDF5BilbyFile, self).test_samples()

    def test_samples_dict(self):
        """Test the samples_dict property of the bilby class
        """
        super(TestCoreHDF5BilbyFile, self).test_samples_dict()

    def test_version(self):
        """Test the version property of the default class
        """
        super(TestCoreHDF5BilbyFile, self).test_version()

    def test_extra_kwargs(self):
        """Test the extra_kwargs property of the default class
        """
        super(TestCoreHDF5BilbyFile, self).test_extra_kwargs()

    def test_injection_parameters(self):
        """Test the injection_parameters property
        """
        true = {par: 1. for par in self.parameters}
        super(TestCoreHDF5BilbyFile, self).test_injection_parameters(true)

    def test_to_dat(self):
        """Test the to_dat method
        """
        super(TestCoreHDF5BilbyFile, self).test_to_dat()

    def test_file_format_read(self):
        """Test that when the file_format is specified, that correct class is used
        """
        super(TestCoreHDF5BilbyFile, self).test_file_format_read(self.path, "bilby")

    def test_downsample(self):
        """Test that the posterior table is correctly downsampled
        """
        super(TestCoreHDF5BilbyFile, self).test_downsample()

    def test_priors(self):
        """Test that the priors are correctly extracted from the bilby result
        file
        """
        super(TestCoreHDF5BilbyFile, self).test_priors(read_function=Read)


class PESummaryFile(BaseRead):
    """Base class to test loading in a PESummary file with the core Read function
    """

    def test_class_name(self):
        """Test the class used to load in this file
        """
        assert isinstance(self.result, pesummary.core.file.formats.pesummary.PESummary)

    def test_parameters(self):
        """Test the parameter property of the PESummary class
        """
        super(PESummaryFile, self).test_parameters(
            self.parameters, pesummary=True)

    def test_samples(self):
        """Test the samples property of the PESummary class
        """
        super(PESummaryFile, self).test_samples(
            self.samples, pesummary=True)

    def test_version(self):
        """Test the version property of the default class
        """
        true = ["No version information found"]
        super(PESummaryFile, self).test_version(true)

    def test_extra_kwargs(self):
        """Test the extra_kwargs property of the default class
        """
        true = [{"sampler": {"log_evidence": 0.5}, "meta_data": {}}]
        super(PESummaryFile, self).test_extra_kwargs(true)

    def test_samples_dict(self):
        """Test the samples_dict property
        """
        assert list(self.result.samples_dict.keys()) == ["label"]

        parameters = self.parameters
        samples = self.samples
        for num, param in enumerate(parameters):
            specific_samples = [i[num] for i in samples]
            drawn_samples = self.result.samples_dict["label"][param]
            assert all(i == j for i, j in zip(drawn_samples, specific_samples))

    def test_to_bilby(self):
        """Test the to_bilby method
        """
        from pesummary.core.file.read import is_bilby_json_file

        bilby_object = self.result.to_bilby(save=False)["label"]
        bilby_object.save_to_file(
            filename=os.path.join(".outdir", "bilby.json"))
        assert is_bilby_json_file(os.path.join(".outdir", "bilby.json"))

    def test_to_dat(self):
        """Test the to_dat method
        """
        self.result.to_dat(
            outdir=".outdir", filenames={"label": "pesummary_label.dat"}
        )
        assert os.path.isfile(os.path.join(".outdir", "pesummary_label.dat"))
        data = np.genfromtxt(
            os.path.join(".outdir", "pesummary_label.dat"), names=True)
        assert all(i in self.parameters for i in list(data.dtype.names))
        assert all(i in list(data.dtype.names) for i in self.parameters)

    def test_downsample(self):
        """Test the .downsample method
        """
        old_samples_dict = self.result.samples_dict
        nsamples = 50
        self.result.downsample(nsamples)
        for num, label in enumerate(self.result.labels):
            assert self.result.samples_dict[label].number_of_samples == nsamples
            for param in self.parameters[num]:
                assert all(
                    samp in old_samples_dict[label][param] for samp in
                    self.result.samples_dict[label][param]
                )
            for idx in range(nsamples):
                samp_inds = [
                    old_samples_dict[label][param].tolist().index(
                        self.result.samples_dict[label][param][idx]
                    ) for param in self.parameters[num]
                ]
                assert len(set(samp_inds)) == 1
            


class TestCoreJsonPESummaryFile(PESummaryFile):
    """Class to test loading in a PESummary json file with the core Read
    function
    """
    def setup(self):
        """Setup the TestCorePESummaryFile class
        """
        if not os.path.isdir(".outdir"):
            os.mkdir(".outdir")
        self.parameters, self.samples = make_result_file(
            extension="json", gw=False, pesummary=True)
        self.result = Read(os.path.join(".outdir", "test.json"))

    def teardown(self):
        """Remove the files and directories created from this class
        """
        if os.path.isdir(".outdir"):
            shutil.rmtree(".outdir")

    def test_class_name(self):
        """Test the class used to load in this file
        """
        super(TestCoreJsonPESummaryFile, self).test_class_name()

    def test_parameters(self):
        """Test the parameter property of the PESummary class
        """
        super(TestCoreJsonPESummaryFile, self).test_parameters()

    def test_samples(self):
        """Test the samples property of the PESummary class
        """
        super(TestCoreJsonPESummaryFile, self).test_samples()

    def test_samples_dict(self):
        """Test the samples_dict property
        """
        super(TestCoreJsonPESummaryFile, self).test_samples_dict()

    def test_version(self):
        """Test the version property of the default class
        """
        super(TestCoreJsonPESummaryFile, self).test_version()

    def test_extra_kwargs(self):
        """Test the extra_kwargs property of the default class
        """
        super(TestCoreJsonPESummaryFile, self).test_extra_kwargs()

    def test_injection_parameters(self):
        """Test the injection_parameters property
        """
        true = {par: float("nan") for par in self.parameters}
        super(TestCoreJsonPESummaryFile, self).test_injection_parameters(
            true, pesummary=True)

    def test_to_bilby(self):
        """Test the to_bilby method
        """
        super(TestCoreJsonPESummaryFile, self).test_to_bilby()

    def test_to_dat(self):
        """Test the to_dat method
        """
        super(TestCoreJsonPESummaryFile, self).test_to_dat()

    def test_file_format_read(self):
        """Test that when the file_format is specified, that correct class is used
        """
        pass

    def test_downsample(self):
        """Test that the posterior table is correctly downsampled
        """
        super(TestCoreJsonPESummaryFile, self).test_downsample()


class TestCoreHDF5PESummaryFile(PESummaryFile):
    """Class to test loading in a PESummary hdf5 file with the core Read
    function
    """
    def setup(self):
        """Setup the TestCorePESummaryFile class
        """
        if not os.path.isdir(".outdir"):
            os.mkdir(".outdir")
        self.parameters, self.samples = make_result_file(
            extension="hdf5", gw=False, pesummary=True)
        self.result = Read(os.path.join(".outdir", "test.h5"))

    def teardown(self):
        """Remove the files and directories created from this class
        """
        if os.path.isdir(".outdir"):
            shutil.rmtree(".outdir")

    def test_class_name(self):
        """Test the class used to load in this file
        """
        super(TestCoreHDF5PESummaryFile, self).test_class_name()

    def test_parameters(self):
        """Test the parameter property of the PESummary class
        """
        super(TestCoreHDF5PESummaryFile, self).test_parameters()

    def test_samples(self):
        """Test the samples property of the PESummary class
        """
        super(TestCoreHDF5PESummaryFile, self).test_samples()

    def test_samples_dict(self):
        """Test the samples_dict property
        """
        super(TestCoreHDF5PESummaryFile, self).test_samples_dict()

    def test_version(self):
        """Test the version property of the default class
        """
        super(TestCoreHDF5PESummaryFile, self).test_version()

    def test_extra_kwargs(self):
        """Test the extra_kwargs property of the default class
        """
        super(TestCoreHDF5PESummaryFile, self).test_extra_kwargs()

    def test_injection_parameters(self):
        """Test the injection_parameters property
        """
        true = {par: float("nan") for par in self.parameters}
        super(TestCoreHDF5PESummaryFile, self).test_injection_parameters(
            true, pesummary=True)

    def test_to_bilby(self):
        """Test the to_bilby method
        """
        super(TestCoreHDF5PESummaryFile, self).test_to_bilby()

    def test_to_dat(self):
        """Test the to_dat method
        """
        super(TestCoreHDF5PESummaryFile, self).test_to_dat()

    def test_file_format_read(self):
        """Test that when the file_format is specified, that correct class is used
        """
        pass

    def test_downsample(self):
        """Test that the posterior table is correctly downsampled
        """
        super(TestCoreHDF5PESummaryFile, self).test_downsample()


class TestGWDatFile(GWBaseRead):
    """Class to test loading in an dat file with the core Read function
    """
    def setup(self):
        """Setup the TestGWDatFile class
        """
        if not os.path.isdir(".outdir"):
            os.mkdir(".outdir")
        self.parameters, self.samples = make_result_file(extension="dat", gw=True)
        self.path = os.path.join(".outdir", "test.dat")
        self.result = GWRead(self.path)

    def teardown(self):
        """Remove the files and directories created from this class
        """
        if os.path.isdir(".outdir"):
            shutil.rmtree(".outdir")

    def test_class_name(self):
        """Test the class used to load in this file
        """
        assert isinstance(self.result, pesummary.gw.file.formats.default.Default)

    def test_parameters(self):
        """Test the parameter property of the default class
        """
        super(TestGWDatFile, self).test_parameters(self.parameters)

    def test_samples(self):
        """Test the samples property of the default class
        """
        super(TestGWDatFile, self).test_samples(self.samples)

    def test_samples_dict(self):
        """Test the samples_dict property of the default class
        """
        true = [self.parameters, self.samples]
        super(TestGWDatFile, self).test_samples_dict(true)

    def test_version(self):
        """Test the version property of the default class
        """
        super(TestGWDatFile, self).test_version()

    def test_extra_kwargs(self):
        """Test the extra_kwargs property of the default class
        """
        super(TestGWDatFile, self).test_extra_kwargs()

    def test_injection_parameters(self):
        """Test the injection_parameters property
        """
        true = {par: float("nan") for par in self.parameters}
        super(TestGWDatFile, self).test_injection_parameters(true)

    def test_to_dat(self):
        """Test the to_dat method
        """
        super(TestGWDatFile, self).test_to_dat()

    def test_to_lalinference_dat(self):
        """Test the to_lalinference dat=True method
        """
        super(TestGWDatFile, self).test_to_lalinference_dat()

    def test_file_format_read(self):
        """Test that when the file_format is specified, that correct class is used
        """
        from pesummary.gw.file.formats.default import Default

        super(TestGWDatFile, self).test_file_format_read(self.path, "dat", Default)

    def test_downsample(self):
        """Test that the posterior table is correctly downsampled
        """
        super(TestGWDatFile, self).test_downsample()


class TestGWHDF5File(GWBaseRead):
    """Class to test loading in an HDF5 file with the gw Read function
    """
    def setup(self):
        """Setup the TestCoreHDF5File class
        """
        if not os.path.isdir(".outdir"):
            os.mkdir(".outdir")
        self.parameters, self.samples = make_result_file(extension="hdf5", gw=True)
        self.path = os.path.join(".outdir", "test.h5")
        self.result = GWRead(self.path)

    def teardown(self):
        """Remove the files and directories created from this class
        """
        if os.path.isdir(".outdir"):
            shutil.rmtree(".outdir")

    def test_class_name(self):
        """Test the class used to load in this file
        """
        assert isinstance(self.result, pesummary.gw.file.formats.default.Default)

    def test_parameters(self):
        """Test the parameter property of the default class
        """
        super(TestGWHDF5File, self).test_parameters(self.parameters)

    def test_samples(self):
        """Test the samples property of the default class
        """
        super(TestGWHDF5File, self).test_samples(self.samples)

    def test_samples_dict(self):
        """Test the samples_dict property of the default class
        """
        true = [self.parameters, self.samples]
        super(TestGWHDF5File, self).test_samples_dict(true)

    def test_version(self):
        """Test the version property of the default class
        """
        super(TestGWHDF5File, self).test_version()

    def test_extra_kwargs(self):
        """Test the extra_kwargs property of the default class
        """
        super(TestGWHDF5File, self).test_extra_kwargs()

    def test_injection_parameters(self):
        """Test the injection_parameters property
        """
        true = {par: float("nan") for par in self.parameters}
        super(TestGWHDF5File, self).test_injection_parameters(true)

    def test_to_dat(self):
        """Test the to_dat method
        """
        super(TestGWHDF5File, self).test_to_dat()

    def test_to_lalinference_dat(self):
        """Test the to_lalinference dat=True method
        """
        super(TestGWHDF5File, self).test_to_lalinference_dat()

    def test_file_format_read(self):
        """Test that when the file_format is specified, that correct class is used
        """
        from pesummary.gw.file.formats.default import Default

        super(TestGWHDF5File, self).test_file_format_read(self.path, "hdf5", Default)

    def test_downsample(self):
        """Test that the posterior table is correctly downsampled
        """
        super(TestGWHDF5File, self).test_downsample()


class TestGWJsonFile(GWBaseRead):
    """Class to test loading in an json file with the gw Read function
    """
    def setup(self):
        """Setup the TestGWDatFile class
        """
        if not os.path.isdir(".outdir"):
            os.mkdir(".outdir")
        self.parameters, self.samples = make_result_file(extension="json", gw=True)
        self.path = os.path.join(".outdir", "test.json")
        self.result = GWRead(self.path)

    def teardown(self):
        """Remove the files and directories created from this class
        """
        if os.path.isdir(".outdir"):
            shutil.rmtree(".outdir")

    def test_class_name(self):
        """Test the class used to load in this file
        """
        assert isinstance(self.result, pesummary.gw.file.formats.default.Default)

    def test_parameters(self):
        """Test the parameter property of the default class
        """
        super(TestGWJsonFile, self).test_parameters(self.parameters)

    def test_samples(self):
        """Test the samples property of the default class
        """
        super(TestGWJsonFile, self).test_samples(self.samples)

    def test_samples_dict(self):
        """Test the samples_dict property of the default class
        """
        true = [self.parameters, self.samples]
        super(TestGWJsonFile, self).test_samples_dict(true)

    def test_version(self):
        """Test the version property of the default class
        """
        super(TestGWJsonFile, self).test_version()

    def test_extra_kwargs(self):
        """Test the extra_kwargs property of the default class
        """
        super(TestGWJsonFile, self).test_extra_kwargs()

    def test_injection_parameters(self):
        """Test the injection_parameters property
        """
        true = {par: float("nan") for par in self.parameters}
        super(TestGWJsonFile, self).test_injection_parameters(true)

    def test_to_dat(self):
        """Test the to_dat method
        """
        super(TestGWJsonFile, self).test_to_dat()

    def test_to_lalinference_dat(self):
        """Test the to_lalinference dat=True method
        """
        super(TestGWJsonFile, self).test_to_lalinference_dat()

    def test_file_format_read(self):
        """Test that when the file_format is specified, that correct class is used
        """
        from pesummary.gw.file.formats.default import Default

        super(TestGWJsonFile, self).test_file_format_read(self.path, "json", Default)

    def test_downsample(self):
        """Test that the posterior table is correctly downsampled
        """
        super(TestGWJsonFile, self).test_downsample()


class TestGWJsonBilbyFile(GWBaseRead):
    """Class to test loading in a bilby json file with the gw Read function
    """
    def setup(self):
        """Setup the TestCoreBilbyFile class
        """
        if not os.path.isdir(".outdir"):
            os.mkdir(".outdir")
        self.parameters, self.samples = make_result_file(
            extension="json", gw=True, bilby=True)
        self.path = os.path.join(".outdir", "test.json")
        self.result = GWRead(self.path)

    def teardown(self):
        """Remove the files and directories created from this class
        """
        if os.path.isdir(".outdir"):
            shutil.rmtree(".outdir")

    def test_class_name(self):
        """Test the class used to load in this file
        """
        assert isinstance(self.result, pesummary.gw.file.formats.bilby.Bilby)

    def test_parameters(self):
        """Test the parameter property of the bilby class
        """
        super(TestGWJsonBilbyFile, self).test_parameters(self.parameters)

    def test_samples(self):
        """Test the samples property of the bilby class
        """
        super(TestGWJsonBilbyFile, self).test_samples(self.samples)

    def test_samples_dict(self):
        """Test the samples_dict property of the bilby class
        """
        true = [self.parameters, self.samples]
        super(TestGWJsonBilbyFile, self).test_samples_dict(true)

    def test_version(self):
        """Test the version property of the default class
        """
        true = "bilby=0.5.3:"
        super(TestGWJsonBilbyFile, self).test_version(true)

    def test_extra_kwargs(self):
        """Test the extra_kwargs property of the default class
        """
        true = {"sampler": {
            "log_bayes_factor": 0.5,
            "log_noise_evidence": 0.1,
            "log_evidence": 0.2,
            "log_evidence_err": 0.1},
            "meta_data": {"time_marginalization": True}}
        super(TestGWJsonBilbyFile, self).test_extra_kwargs(true)

    def test_injection_parameters(self):
        """Test the injection_parameters property
        """
        true = {par: 1. for par in self.parameters}
        super(TestGWJsonBilbyFile, self).test_injection_parameters(true)

    def test_to_dat(self):
        """Test the to_dat method
        """
        super(TestGWJsonBilbyFile, self).test_to_dat()

    def test_to_lalinference_dat(self):
        """Test the to_lalinference dat=True method
        """
        super(TestGWJsonBilbyFile, self).test_to_lalinference_dat()

    def test_file_format_read(self):
        """Test that when the file_format is specified, that correct class is used
        """
        from pesummary.gw.file.formats.bilby import Bilby

        super(TestGWJsonBilbyFile, self).test_file_format_read(self.path, "bilby", Bilby)

    def test_downsample(self):
        """Test that the posterior table is correctly downsampled
        """
        super(TestGWJsonBilbyFile, self).test_downsample()

    def test_priors(self, read_function=GWRead):
        """Test that the priors are correctly extracted from the bilby result
        file
        """
        assert "final_mass_source_non_evolved" not in self.result.parameters
        for param, prior in self.result.priors["samples"].items():
            assert isinstance(prior, np.ndarray)
        assert "final_mass_source_non_evolved" in self.result.priors["samples"].keys()
        f = read_function(self.path, disable_prior_conversion=True)
        assert "final_mass_source_non_evolved" not in f.priors["samples"].keys()
        f = read_function(self.path, disable_prior=True)
        assert not hasattr(f, "priors")


class TestGWLALInferenceFile(GWBaseRead):
    """Class to test loading in a LALInference file with the gw Read function
    """
    def setup(self):
        """Setup the TestCoreBilbyFile class
        """
        if not os.path.isdir(".outdir"):
            os.mkdir(".outdir")
        self.parameters, self.samples = make_result_file(
            extension="hdf5", gw=True, lalinference=True)
        self.path = os.path.join(".outdir", "test.hdf5")
        self.result = GWRead(self.path)

    def teardown(self):
        """Remove the files and directories created from this class
        """
        if os.path.isdir(".outdir"):
            shutil.rmtree(".outdir")

    def test_class_name(self):
        """Test the class used to load in this file
        """
        assert isinstance(
            self.result, pesummary.gw.file.formats.lalinference.LALInference)

    def test_parameters(self):
        """Test the parameter property of the bilby class
        """
        super(TestGWLALInferenceFile, self).test_parameters(self.parameters)

    def test_samples(self):
        """Test the samples property of the bilby class
        """
        super(TestGWLALInferenceFile, self).test_samples(self.samples)

    def test_samples_dict(self):
        """Test the samples_dict property of the bilby class
        """
        true = [self.parameters, self.samples]
        super(TestGWLALInferenceFile, self).test_samples_dict(true)

    def test_version(self):
        """Test the version property of the default class
        """
        super(TestGWLALInferenceFile, self).test_version()

    def test_extra_kwargs(self):
        """Test the extra_kwargs property of the default class
        """
        true = {"sampler": {"nsamples": 1000}, "meta_data": {}, "other": {}}
        super(TestGWLALInferenceFile, self).test_extra_kwargs(true=true)

    def test_injection_parameters(self):
        """Test the injection_parameters property
        """
        super(TestGWLALInferenceFile, self).test_injection_parameters(None)

    def test_to_dat(self):
        """Test the to_dat method
        """
        super(TestGWLALInferenceFile, self).test_to_dat()

    def test_to_lalinference_dat(self):
        """Test the to_lalinference dat=True method
        """
        super(TestGWLALInferenceFile, self).test_to_lalinference_dat()

    def test_file_format_read(self):
        """Test that when the file_format is specified, that correct class is used
        """
        from pesummary.gw.file.formats.lalinference import LALInference

        super(TestGWLALInferenceFile, self).test_file_format_read(
            self.path, "lalinference", LALInference
        )

    def test_downsample(self):
        """Test that the posterior table is correctly downsampled
        """
        super(TestGWLALInferenceFile, self).test_downsample()