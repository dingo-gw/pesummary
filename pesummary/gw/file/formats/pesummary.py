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

from pesummary.gw.file.formats.base_read import GWRead
from pesummary.core.file.formats.pesummary import (
    PESummary as CorePESummary, PESummaryDeprecated as CorePESummaryDeprecated,
    deprecation_warning
)
from pesummary.utils.utils import logger
import numpy as np
import warnings


class PESummary(GWRead, CorePESummary):
    """This class handles the existing posterior_samples.h5 file

    Parameters
    ----------
    parser: argparser
        The parser containing the command line arguments

    Attributes
    ----------
    existing_file: str
        the path to the existing posterior_samples.h5 file
    existing_approximants: list
        list of approximants that have been used in the previous analysis
    existing_labels: list
        list of labels that have been used in the previous analysis
    existing_samples: nd list
        nd list of samples stored for each approximant used in the previous
        analysis
    """
    def __init__(self, path_to_results_file, **kwargs):
        super(PESummary, self).__init__(
            path_to_results_file=path_to_results_file
        )

    @property
    def load_kwargs(self):
        return dict(grab_data_from_dictionary=self._grab_data_from_dictionary)

    def load(self, function, **kwargs):
        """Load a results file according to a given function

        Parameters
        ----------
        function: func
            callable function that will load in your results file
        """
        data = self.load_from_function(
            function, self.path_to_results_file, **kwargs)
        self.data = data
        if "version" in data.keys() and data["version"] is not None:
            self.input_version = data["version"]
        else:
            self.input_version = "No version information found"
        if "kwargs" in data.keys():
            self.extra_kwargs = data["kwargs"]
        else:
            self.extra_kwargs = {"sampler": {}, "meta_data": {}}
            self.extra_kwargs["sampler"]["nsamples"] = len(self.data["samples"])
        if data["injection"] is not None:
            self.injection_parameters = data["injection"]
        if "prior" in data.keys() and data["prior"] != {}:
            self.priors = data["prior"]
        if "weights" in self.data.keys():
            self.weights = self.data["weights"]
        if "approximant" in self.data.keys():
            self.approximant = self.data["approximant"]
        if "labels" in self.data.keys():
            self.labels = self.data["labels"]
        if "config" in self.data.keys():
            self.config = self.data["config"]
        if "psd" in self.data.keys():
            from pesummary.gw.file.psd import PSD

            try:
                self.psd = {
                    label: {
                        ifo: PSD(value) for ifo, value in psd_data.items()
                    } for label, psd_data in self.data["psd"].items()
                }
            except (KeyError, AttributeError):
                self.psd = self.data["psd"]
        if "calibration" in self.data.keys():
            from pesummary.gw.file.calibration import Calibration

            try:
                self.calibration = {
                    label: {
                        ifo: Calibration(value) for ifo, value in
                        calibration_data.items()
                    } for label, calibration_data in
                    self.data["calibration"].items()
                }
            except (KeyError, AttributeError):
                self.calibration = self.data["calibration"]

    @staticmethod
    def _grab_data_from_dictionary(dictionary):
        """
        """
        stored_data = CorePESummary._grab_data_from_dictionary(
            dictionary=dictionary
        )

        approx_list = list()
        psd_dict, cal_dict = {}, {}
        psd, cal = None, None
        for num, label in enumerate(stored_data["labels"]):
            data, = GWRead.load_recursively(label, dictionary)
            if "psds" in data.keys():
                psd_dict[label] = data["psds"]
            if "calibration_envelope" in data.keys():
                cal_dict[label] = data["calibration_envelope"]
            if "approximant" in data.keys():
                approx_list.append(data["approximant"])
            else:
                approx_list.append(None)
        stored_data["approximant"] = approx_list
        stored_data["calibration"] = cal_dict
        stored_data["psd"] = psd_dict
        return stored_data

    @property
    def calibration_data_in_results_file(self):
        if self.calibration:
            keys = [list(self.calibration[i].keys()) for i in self.labels]
            total = [[self.calibration[key][ifo] for ifo in keys[num]] for
                     num, key in enumerate(self.labels)]
            return total, keys
        return None

    @property
    def detectors(self):
        det_list = list()
        for parameters in self.parameters:
            detectors = list()
            for param in parameters:
                if "_optimal_snr" in param and param != "network_optimal_snr":
                    detectors.append(param.split("_optimal_snr")[0])
            if not detectors:
                detectors.append(None)
            det_list.append(detectors)
        return det_list

    def generate_all_posterior_samples(self):
        from pesummary.gw.file.conversions import _Conversion

        converted_params, converted_samples = [], []
        for param, samples, kwargs in zip(
                self.parameters, self.samples, self.extra_kwargs
        ):
            parameters, samples = _Conversion(
                param, samples, extra_kwargs=kwargs, return_dict=False
            )
            converted_params.append(parameters)
            converted_samples.append(samples)
        self.data["parameters"] = converted_params
        self.data["samples"] = converted_samples

    def to_bilby(self):
        """Convert a PESummary metafile to a bilby results object
        """
        from bilby.gw.result import CompactBinaryCoalescenceResult
        from bilby.core.prior import Prior, PriorDict
        from pandas import DataFrame

        objects = dict()
        for num, label in enumerate(self.labels):
            priors = PriorDict()
            logger.warn(
                "No prior information is known so setting it to a default")
            priors.update({parameter: Prior() for parameter in self.parameters[num]})
            posterior_data_frame = DataFrame(
                self.samples[num], columns=self.parameters[num])
            meta_data = {
                "likelihood": {
                    "waveform_arguments": {
                        "waveform_approximant": self.approximant[num]},
                    "interferometers": self.detectors[num]}}
            bilby_object = CompactBinaryCoalescenceResult(
                search_parameter_keys=self.parameters[num],
                posterior=posterior_data_frame, label="pesummary_%s" % label,
                samples=self.samples[num], priors=priors, meta_data=meta_data)
            objects[label] = bilby_object
        return objects

    def to_lalinference(
        self, outdir="./", labels=None, overwrite=False,
        sampler="lalinference_nest"
    ):
        """Save a PESummary metafile as a lalinference hdf5 file

        Parameters
        ----------
        outdir: str
            The directory where you would like to write the lalinference file
        labels: list
            The labels for the runs that you wish to write to file
        overwrite: Bool
            If True, an existing file of the same name will be overwritten
        sampler: str
            The sampler which you wish to store in the result file. This may
            either be 'lalinference_nest' or 'lalinference_mcmc'
        """
        from pesummary.gw.file.formats.lalinference import write_to_file
        import h5py

        if labels is not None:
            for label in labels:
                if label not in self.labels:
                    raise ValueError(
                        "The label '{}' does not exist in the metafile".format(
                            label
                        )
                    )
        else:
            labels = self.labels

        for num, label in enumerate(labels):
            write_to_file(
                self.samples_dict[label], outdir=outdir, label=label,
                overwrite=overwrite, sampler=sampler
            )


class PESummaryDeprecated(PESummary):
    """
    """
    def __init__(self, path_to_results_file):
        warnings.warn(deprecation_warning)
        super(PESummaryDeprecated, self).__init__(path_to_results_file)

    @property
    def load_kwargs(self):
        return {
            "grab_data_from_dictionary": PESummaryDeprecated._grab_data_from_dictionary
        }

    @staticmethod
    def _grab_data_from_dictionary(dictionary):
        """
        """
        data = CorePESummaryDeprecated._grab_data_from_dictionary(
            dictionary=dictionary
        )

        approx_list = list()
        psd, cal = None, None
        for num, key in enumerate(data["labels"]):
            if "psds" in dictionary.keys():
                psd, = GWRead.load_recursively("psds", dictionary)
            if "calibration_envelope" in dictionary.keys():
                cal, = GWRead.load_recursively("calibration_envelope", dictionary)
            if "approximant" in dictionary.keys():
                if key in dictionary["approximant"].keys():
                    approx_list.append(dictionary["approximant"][key])
                else:
                    approx_list.append(None)
            else:
                approx_list.append(None)
        data["approximant"] = approx_list
        data["calibration"] = cal
        data["psd"] = psd

        return data
