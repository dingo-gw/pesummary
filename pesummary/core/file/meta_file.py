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

import inspect
import os
import numpy as np
import json
import copy

import pesummary
from pesummary import __version__
from pesummary.core.inputs import PostProcessing
from pesummary.utils.utils import make_dir, logger
from pesummary import conf

DEFAULT_HDF5_KEYS = ["config_file", "injection_data", "version", "meta_data", "priors"]


def recursively_save_dictionary_to_hdf5_file(
        f, dictionary, current_path=None, extra_keys=None
):
    """Recursively save a dictionary to a hdf5 file

    Parameters
    ----------
    f: h5py._hl.files.File
        the open hdf5 file that you would like the data to be saved to
    dictionary: dict
        dictionary of data
    current_path: optional, str
        string to indicate the level to save the data in the hdf5 file
    """
    def _safe_create_hdf5_group(hdf5_file, key):
        if key not in hdf5_file.keys():
            hdf5_file.create_group(key)
    if extra_keys is None:
        extra_keys = DEFAULT_HDF5_KEYS
    _safe_create_hdf5_group(hdf5_file=f, key="posterior_samples")
    for key in extra_keys:
        if key in dictionary:
            _safe_create_hdf5_group(hdf5_file=f, key=key)
    if current_path is None:
        current_path = []

    for k, v in dictionary.items():
        if isinstance(v, dict):
            if k not in f["/" + "/".join(current_path)].keys():
                f["/".join(current_path)].create_group(k)
            path = current_path + [k]
            recursively_save_dictionary_to_hdf5_file(f, v, path, extra_keys=extra_keys)
        else:
            create_hdf5_dataset(key=k, value=v, hdf5_file=f, current_path=current_path)


def create_hdf5_dataset(key, value, hdf5_file, current_path):
    """
    Create a hdf5 dataset in place

    Parameters
    ----------
    key: str
        Key for the new dataset
    value: array-like
        Data to store
    hdf5_file: h5py.File
        hdf5 file object
    current_path: str
        Current string withing the hdf5 file
    """
    error_message = "Cannot process {}={} from list with type {} for hdf5"
    array_types = (list, pesummary.utils.utils.Array, np.ndarray)
    numeric_types = (float, int, np.number)
    string_types = (str, bytes)
    if isinstance(value, array_types):
        import math

        if not len(value):
            data = np.array([])
        elif isinstance(value[0], string_types):
            data = np.array(value, dtype="S")
        elif isinstance(value[0], array_types):
            data = np.array(np.vstack(value))
        elif isinstance(value[0], (tuple, np.record)):
            data = value
        elif math.isnan(value[0]):
            data = np.array(["NaN"] * len(value), dtype="S")
        elif isinstance(value[0], numeric_types):
            data = np.array(value)
        else:
            raise TypeError(error_message.format(key, value, type(value[0])))
    elif isinstance(value, string_types):
        data = np.array([value], dtype="S")
    elif isinstance(value, numeric_types):
        data = np.array([value])
    elif value == {}:
        data = np.array(np.array("NaN"))
    elif inspect.isclass(value) or inspect.isfunction(value):
        data = np.array([value.__module__ + value.__name__], dtype="S")
    elif inspect.ismodule(value):
        data = np.array([value.__name__], dtype="S")
    else:
        raise TypeError(error_message.format(key, value, type(value)))
    hdf5_file["/".join(current_path)].create_dataset(key, data=data)


class PESummaryJsonEncoder(json.JSONEncoder):
    """Personalised JSON encoder for PESummary
    """
    def default(self, obj):
        """Return a json serializable object for 'obj'

        Parameters
        ----------
        obj: object
            object you wish to make json serializable
        """
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if inspect.isfunction(obj):
            return str(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, (np.bool, np.bool_, bool)):
            return str(obj)
        elif isinstance(obj, type):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class _MetaFile(object):
    """This is a base class to handle the functions to generate a meta file
    """
    def __init__(
        self, samples, labels, config, injection_data, file_versions,
        file_kwargs, webdir=None, result_files=None, hdf5=False, priors={},
        existing_version=None, existing_label=None, existing_samples=None,
        existing_injection=None, existing_metadata=None, existing_config=None,
        existing_priors={}, existing_metafile=None, outdir=None, existing=None
    ):
        self.data = {}
        self.webdir = webdir
        self.result_files = result_files
        self.samples = samples
        self.labels = labels
        self.config = config
        self.injection_data = injection_data
        self.file_versions = file_versions
        self.file_kwargs = file_kwargs
        self.hdf5 = hdf5
        self.priors = priors
        self.existing_version = existing_version
        self.existing_labels = existing_label
        self.existing_samples = existing_samples
        self.existing_injection = existing_injection
        self.existing_file_kwargs = existing_metadata
        self.existing_config = existing_config
        self.existing_priors = existing_priors
        self.existing_metafile = existing_metafile
        self.existing = existing
        self.outdir = outdir

        if self.existing_labels is None:
            self.existing_labels = [None]
        if self.existing is not None:
            self.add_existing_data()

    @property
    def outdir(self):
        return self._outdir

    @outdir.setter
    def outdir(self, outdir):
        if outdir is not None:
            self._outdir = os.path.abspath(outdir)
        elif self.webdir is not None:
            self._outdir = os.path.join(self.webdir, "samples")
        else:
            raise Exception("Please provide an output directory for the data")

    @property
    def file_name(self):
        base = "posterior_samples.{}"
        if self.hdf5:
            return base.format("h5")
        return base.format("json")

    @property
    def meta_file(self):
        return os.path.join(self.outdir, self.file_name)

    def make_dictionary(self):
        """Wrapper function for _make_dictionary
        """
        self._make_dictionary()

    def _make_dictionary(self):
        """Generate a single dictionary which stores all information
        """
        dictionary = {
            "posterior_samples": {},
            "injection_data": {},
            "version": {},
            "meta_data": {},
            "priors": {},
            "config_file": {}
        }

        dictionary["priors"] = self.priors
        for num, label in enumerate(self.labels):
            parameters = self.samples[label].keys()
            samples = np.array([self.samples[label][i] for i in parameters]).T
            dictionary["posterior_samples"][label] = {
                "parameter_names": list(parameters),
                "samples": samples.tolist()
            }

            dictionary["injection_data"][label] = {
                "injection_values": [
                    self.injection_data[label][i] for i in
                    parameters
                ]
            }

            dictionary["version"][label] = [self.file_versions[label]]
            dictionary["version"]["pesummary"] = [__version__]
            dictionary["meta_data"][label] = self.file_kwargs[label]

            if self.config != {} and self.config[num] is not None and not isinstance(self.config[num], dict):
                config = self._grab_config_data_from_data_file(self.config[num])
                dictionary["config_file"][label] = config
            elif self.config[num] is not None:
                dictionary["config_file"][label] = self.config[num]
        self.data = dictionary

    @staticmethod
    def _grab_config_data_from_data_file(file):
        """Return the config data as a dictionary

        Parameters
        ----------
        file: str
            path to the configuration file
        """
        import configparser

        data = {}
        config = configparser.ConfigParser()
        try:
            config.read(file)
            sections = config.sections()
        except Exception as e:
            sections = None
            logger.info(
                "Unable to open %s because %s. The data will not be stored in "
                "the meta file" % (file, e)
            )
        if sections:
            for i in sections:
                data[i] = {}
                for key in config["%s" % (i)]:
                    data[i][key] = config["%s" % (i)]["%s" % (key)]
        return data

    @staticmethod
    def write_to_dat(file_name, samples, header=None):
        """Write samples to a .dat file

        Parameters
        ----------
        file_name: str
            the name of the file that you wish to write the samples to
        samples: np.ndarray
            1d/2d array of samples to write to file
        header: list, optional
            List of strings to write at the beginning of the file
        """
        np.savetxt(
            file_name, samples, delimiter=conf.delimiter,
            header=conf.delimiter.join(header), comments=""
        )

    @staticmethod
    def _convert_posterior_samples_to_numpy(dictionary):
        """Convert the posterior samples from a column-major dictionary
        to a row-major numpy array

        Parameters
        ----------
        dictionary: dict
            nested dictionary of posterior samples to convert to a numpy array.
            Each set of column-major posterior samples should be an item for
            a given label

        Examples
        --------
        >>> dictionary = {"label": {"mass_1": [1,2,3], "mass_2": [1,2,3]}}
        >>> dictionry = _Metafile._convert_posterior_samples_to_numpy(
        ...     dictionary
        ... )
        >>> print(dictionary)
        ... {'label': rec.array([(1., 1.), (2., 2.), (3., 3.)],
        ...           dtype=[('mass_1', '<f4'), ('mass_2', '<f4')])}
        """
        from pandas import DataFrame

        samples = copy.deepcopy(dictionary)
        for label, item in samples.items():
            samples[label] = item.to_structured_array()
        return samples

    def write_marginalized_posterior_to_dat(self):
        """Write the marginalized posterior for each parameter to a .dat file
        """
        for label in self.labels:
            if not os.path.isdir(os.path.join(self.outdir, label)):
                make_dir(os.path.join(self.outdir, label))
            for param, samples in self.samples[label].items():
                self.write_to_dat(
                    os.path.join(
                        self.outdir, label, "{}_{}.dat".format(label, param)
                    ), samples, header=[param]
                )

    def save_to_json(self):
        """Save the metafile as a json file
        """
        with open(self.meta_file, "w") as f:
            json.dump(
                self.data, f, indent=4, sort_keys=True,
                cls=PESummaryJsonEncoder
            )

    def save_to_hdf5(self):
        """Save the metafile as a hdf5 file
        """
        import h5py

        key = "posterior_samples"
        self.data[key] = self._convert_posterior_samples_to_numpy(
            self.samples
        )
        with h5py.File(self.meta_file, "w") as f:
            recursively_save_dictionary_to_hdf5_file(
                f, self.data, extra_keys=DEFAULT_HDF5_KEYS
            )

    def save_to_dat(self):
        """Save the samples to a .dat file
        """
        for label in self.labels:
            parameters = self.samples[label].keys()
            samples = np.array([self.samples[label][i] for i in parameters])
            self.write_to_dat(
                os.path.join(self.outdir, "{}_pesummary.dat".format(label)),
                samples.T, header=parameters
            )

    def add_existing_data(self):
        """
        """
        from pesummary.utils.utils import _add_existing_data

        self = _add_existing_data(self)


class MetaFile(PostProcessing):
    """This class handles the creation of a metafile storing all information
    from the analysis
    """
    def __init__(self, inputs):
        from pesummary.utils.utils import logger

        super(MetaFile, self).__init__(inputs)
        logger.info("Starting to generate the meta file")
        meta_file = _MetaFile(
            self.samples, self.labels, self.config,
            self.injection_data, self.file_version, self.file_kwargs,
            hdf5=self.hdf5, webdir=self.webdir, result_files=self.result_files,
            existing_version=self.existing_file_version, existing_label=self.existing_labels,
            existing_samples=self.existing_samples,
            existing_injection=self.existing_injection_data,
            existing_metadata=self.existing_file_kwargs,
            existing_config=self.existing_config, existing=self.existing,
            existing_priors=self.existing_priors,
            existing_metafile=self.existing_metafile
        )
        meta_file.make_dictionary()
        if not self.hdf5:
            meta_file.save_to_json()
        else:
            meta_file.save_to_hdf5()
        meta_file.save_to_dat()
        meta_file.write_marginalized_posterior_to_dat()
        logger.info(
            "Finishing generating the meta file. The meta file can be viewed "
            "here: {}".format(meta_file.meta_file)
        )
