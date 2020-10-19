#! /usr/bin/env python

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

from pesummary.utils.utils import logger, gw_results_file
from pesummary.core.inputs import PostProcessing
from pesummary.gw.inputs import GWPostProcessing


class WebpageGeneration(object):
    """Wrapper class for _GWWebpageGeneration and _CoreWebpageGeneration

    Parameters
    ----------
    inputs: argparse.Namespace
        Namespace object containing the command line options
    colors: list, optional
        colors that you wish to use to distinguish different result files
    """
    def __init__(self, inputs, colors="default", gw=False):
        self.inputs = inputs
        self.colors = colors
        self.gw = gw
        self.generate_webpages()

    def generate_webpages(self):
        """Generate all plots for all result files passed
        """
        logger.info("Starting to generate webpages")
        if self.gw and self.inputs.public:
            object = _PublicGWWebpageGeneration(self.inputs, colors=self.colors)
        elif self.gw:
            object = _GWWebpageGeneration(self.inputs, colors=self.colors)
        else:
            object = _CoreWebpageGeneration(self.inputs, colors=self.colors)
        object.generate_webpages()
        logger.info("Finished generating webpages")


class _CoreWebpageGeneration(PostProcessing):
    """Class to generate all webpages for all result files with the Core module

    Parameters
    ----------
    inputs: argparse.Namespace
        Namespace object containing the command line options
    colors: list, optional
        colors that you wish to use to distinguish different result files
    """
    def __init__(self, inputs, colors="default"):
        from pesummary.core.webpage.main import _WebpageGeneration

        super(_CoreWebpageGeneration, self).__init__(inputs, colors)
        key_data = self.grab_key_data_from_result_files()
        self.webpage_object = _WebpageGeneration(
            webdir=self.webdir, samples=self.samples, labels=self.labels,
            publication=self.publication, user=self.user, config=self.config,
            same_parameters=self.same_parameters, base_url=self.baseurl,
            file_versions=self.file_version, hdf5=self.hdf5, colors=self.colors,
            custom_plotting=self.custom_plotting,
            existing_labels=self.existing_labels,
            existing_config=self.existing_config,
            existing_file_version=self.existing_file_version,
            existing_injection_data=self.existing_injection_data,
            existing_samples=self.existing_samples,
            existing_metafile=self.existing,
            existing_file_kwargs=self.existing_file_kwargs,
            existing_weights=self.existing_weights,
            add_to_existing=self.add_to_existing, notes=self.notes,
            disable_comparison=self.disable_comparison,
            disable_interactive=self.disable_interactive,
            package_information=self.package_information,
            mcmc_samples=self.mcmc_samples,
            external_hdf5_links=self.external_hdf5_links, key_data=key_data
        )

    def generate_webpages(self):
        """Generate all webpages within the Core module
        """
        self.webpage_object.generate_webpages()


class _GWWebpageGeneration(GWPostProcessing):
    """Class to generate all webpages for all result files with the GW module

    Parameters
    ----------
    inputs: argparse.Namespace
        Namespace object containing the command line options
    colors: list, optional
        colors that you wish to use to distinguish different result files
    """
    def __init__(self, inputs, colors="default"):
        from pesummary.gw.webpage.main import _WebpageGeneration

        super(_GWWebpageGeneration, self).__init__(inputs, colors)
        key_data = self.grab_key_data_from_result_files()
        self.webpage_object = _WebpageGeneration(
            webdir=self.webdir, samples=self.samples, labels=self.labels,
            publication=self.publication, user=self.user, config=self.config,
            same_parameters=self.same_parameters, base_url=self.baseurl,
            file_versions=self.file_version, hdf5=self.hdf5, colors=self.colors,
            custom_plotting=self.custom_plotting, gracedb=self.gracedb,
            pepredicates_probs=self.pepredicates_probs,
            approximant=self.approximant, key_data=key_data,
            file_kwargs=self.file_kwargs, existing_labels=self.existing_labels,
            existing_config=self.existing_config,
            existing_file_version=self.existing_file_version,
            existing_injection_data=self.existing_injection_data,
            existing_samples=self.existing_samples,
            existing_metafile=self.existing,
            add_to_existing=self.add_to_existing,
            existing_file_kwargs=self.existing_file_kwargs,
            existing_weights=self.existing_weights,
            result_files=self.result_files, notes=self.notes,
            disable_comparison=self.disable_comparison,
            disable_interactive=self.disable_interactive,
            pastro_probs=self.pastro_probs, gwdata=self.gwdata,
            publication_kwargs=self.publication_kwargs,
            no_ligo_skymap=self.no_ligo_skymap,
            psd=self.psd, priors=self.priors,
            package_information=self.package_information,
            mcmc_samples=self.mcmc_samples,
            external_hdf5_links=self.external_hdf5_links
        )

    def generate_webpages(self):
        """Generate all webpages within the Core module
        """
        self.webpage_object.generate_webpages()


class _PublicGWWebpageGeneration(GWPostProcessing):
    """Class to generate all webpages for all result files with the GW module

    Parameters
    ----------
    inputs: argparse.Namespace
        Namespace object containing the command line options
    colors: list, optional
        colors that you wish to use to distinguish different result files
    """
    def __init__(self, inputs, colors="default"):
        from pesummary.gw.webpage.public import _PublicWebpageGeneration

        super(_PublicGWWebpageGeneration, self).__init__(inputs, colors)
        key_data = self.grab_key_data_from_result_files()
        self.webpage_object = _PublicWebpageGeneration(
            webdir=self.webdir, samples=self.samples, labels=self.labels,
            publication=self.publication, user=self.user, config=self.config,
            same_parameters=self.same_parameters, base_url=self.baseurl,
            file_versions=self.file_version, hdf5=self.hdf5, colors=self.colors,
            custom_plotting=self.custom_plotting, gracedb=self.gracedb,
            pepredicates_probs=self.pepredicates_probs,
            approximant=self.approximant, key_data=key_data,
            file_kwargs=self.file_kwargs, existing_labels=self.existing_labels,
            existing_config=self.existing_config,
            existing_file_version=self.existing_file_version,
            existing_injection_data=self.existing_injection_data,
            existing_samples=self.existing_samples,
            existing_metafile=self.existing,
            add_to_existing=self.add_to_existing,
            existing_file_kwargs=self.existing_file_kwargs,
            existing_weights=self.existing_weights,
            result_files=self.result_files, notes=self.notes,
            disable_comparison=self.disable_comparison,
            disable_interactive=self.disable_interactive,
            pastro_probs=self.pastro_probs, gwdata=self.gwdata,
            publication_kwargs=self.publication_kwargs,
            no_ligo_skymap=self.no_ligo_skymap,
            psd=self.psd, priors=self.priors,
            package_information=self.package_information,
            mcmc_samples=self.mcmc_samples,
            external_hdf5_links=self.external_hdf5_links
        )

    def generate_webpages(self):
        """Generate all webpages within the Core module
        """
        self.webpage_object.generate_webpages()


def main(args=None):
    """Top level interface for `summarypages`
    """
    from pesummary.gw.parser import parser
    from pesummary.utils import functions, history_dictionary

    _parser = parser()
    opts, unknown = _parser.parse_known_args(args=args)
    func = functions(opts)
    args = func["input"](opts)
    from .summaryplots import PlotGeneration

    plotting_object = PlotGeneration(args, gw=gw_results_file(opts))
    WebpageGeneration(args, gw=gw_results_file(opts))
    _history = history_dictionary(
        program=_parser.prog, creator=args.user,
        command_line=_parser.command_line
    )
    func["MetaFile"](args, history=_history)
    if gw_results_file(opts):
        kwargs = dict(ligo_skymap_PID=plotting_object.ligo_skymap_PID)
    else:
        kwargs = {}
    func["FinishingTouches"](args, **kwargs)


if __name__ == "__main__":
    main()
