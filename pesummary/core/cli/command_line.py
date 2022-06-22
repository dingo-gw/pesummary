# Licensed under an MIT style license -- see LICENSE.md

import argparse
from pesummary import conf
from .actions import ConfigAction, CheckFilesExistAction, DictionaryAction

__author__ = ["Charlie Hoy <charlie.hoy@ligo.org>"]


def _core_command_line_arguments(parser):
    """Add core command line options to the Argument Parser

    Parameters
    ----------
    parser: object
        OptionParser instance
    """
    core_group = parser.add_argument_group(
        "Core command line options\n"
        "-------------------------"
    )
    core_group.add_argument(
        "pesummary", nargs='?', action=ConfigAction,
        help="configuration file containing the command line arguments"
    )
    core_group.add_argument(
        "-w", "--webdir", dest="webdir", default=None, metavar="DIR",
        help="make page and plots in DIR"
    )
    core_group.add_argument(
        "-b", "--baseurl", dest="baseurl", metavar="DIR", default=None,
        help="make the page at this url"
    )
    core_group.add_argument(
        "--labels", dest="labels", help="labels used to distinguish runs",
        nargs='+', default=None
    )
    core_group.add_argument(
        "-s", "--samples", dest="samples", default=None, nargs='+',
        action=CheckFilesExistAction, help=(
            "Path to posterior samples file(s). See documentation for allowed "
            "formats. If path is on a remote server, add username and "
            "servername in the form {username}@{servername}:{path}. If path "
            "is on a public webpage, ensure the path starts with https://. "
            "You may also pass a string such as posterior_samples*.dat and "
            "all matching files will be used"
        )
    )
    core_group.add_argument(
        "-c", "--config", dest="config", nargs='+', default=None,
        action=CheckFilesExistAction, help=(
            "configuration file associcated with each samples file."
        )
    )
    core_group.add_argument(
        "--email", action="store", default=None,
        help=(
            "send an e-mail to the given address with a link to the finished "
            "page."
        )
    )
    core_group.add_argument(
        "-i", "--inj_file", dest="inj_file", nargs='+', default=None,
        action=CheckFilesExistAction, help="path to injetcion file"
    )
    core_group.add_argument(
        "--user", dest="user", help=argparse.SUPPRESS, default=conf.user
    )
    core_group.add_argument(
        "--testing", action="store_true", help=argparse.SUPPRESS, default=False
    )
    core_group.add_argument(
        "--add_to_existing", action="store_true", default=False,
        help="add new results to an existing html page"
    )
    core_group.add_argument(
        "-e", "--existing_webdir", dest="existing", default=None,
        help="web directory of existing output"
    )
    core_group.add_argument(
        "--seed", dest="seed", default=123456789, type=int,
        help="Random seed to used through the analysis. Default 123456789"
    )
    core_group.add_argument(
        "-v", "--verbose", action="store_true",
        help="print useful information for debugging purposes"
    )
    core_group.add_argument(
        "--preferred", dest="preferred", default=None, help=(
            "label of the preferred run. If only one result file is passed "
            "this label is the preferred analysis by default"
        )
    )
    return core_group


def _samples_command_line_arguments(parser):
    """Add sample specific command line options to the Argument Parser

    Parameters
    ----------
    parser: object
        OptionParser instance
    """
    sample_group = parser.add_argument_group(
        "Options specific to the samples you wish to input\n"
        "-------------------------------------------------"
    )
    sample_group.add_argument(
        "--ignore_parameters", dest="ignore_parameters", nargs='+', default=None,
        help=(
            "Parameters that you wish to not include in the summarypages. You "
            "may list them or use wildcards ('recalib*')"
        )
    )
    sample_group.add_argument(
        "--nsamples", dest="nsamples", default=None, help=(
            "The number of samples to use and store in the PESummary metafile. "
            "These samples will be randomly drawn from the posterior "
            "distributions"
        )
    )
    sample_group.add_argument(
        "--keep_nan_likelihood_samples", dest="keep_nan_likelihood_samples",
        action="store_true", default=False, help=(
            "Do not remove posterior samples where the likelihood='nan'. "
            "Without this option, posterior samples where the likelihood='nan' "
            "are removed by default."
        )
    )
    sample_group.add_argument(
        "--burnin", dest="burnin", default=None, help=(
            "Number of samples to remove as burnin"
        )
    )
    sample_group.add_argument(
        "--burnin_method", dest="burnin_method", default=None, help=(
            "The algorithm to use to remove mcmc samples as burnin. This is "
            "only used when `--mcmc_samples` also used"
        )
    )
    sample_group.add_argument(
        "--regenerate", dest="regenerate", default=None, nargs="+", help=(
            "List of posterior distributions that you wish to regenerate if "
            "possible"
        )
    )
    sample_group.add_argument(
        "--mcmc_samples", action="store_true", default=False, help=(
            "treat the passed samples as seperate mcmc chains for the same "
            "analysis"
        )
    )
    sample_group.add_argument(
        "--path_to_samples", default=None, nargs="+", help=(
            "Path to the posterior samples stored in the result file. If "
            "None, pesummary will search for a 'posterior' or "
            "'posterior_samples' group. If more than one result file is "
            "passed, and only the third file requires a path_to_samples "
            "provide --path_to_samples None None path/to/samples"
        )
    )
    sample_group.add_argument(
        "--pe_algorithm", default=None, nargs="+", help=(
            "Name of the algorithm used to generate the result file"
        )
    )
    sample_group.add_argument(
        "--reweight_samples", default=False, help=(
            "Method to use when reweighting posterior and/or prior samples. "
            "Default do not reweight samples."
        )
    )
    sample_group.add_argument(
        "--descriptions", default={}, action=DictionaryAction, nargs="+",
        help=(
            "JSON file containing a set of descriptions for each analysis or "
            "dictionary giving descriptions for each analysis directly from "
            "the command line (e.g. `--descriptions label1:'description'`). "
            "These descriptions are then saved in the output."
        )
    )
    return sample_group


def _plotting_command_line_arguments(parser):
    """Add specific command line options for plotting options

    Parameters
    ----------
    parser: object
        OptionParser instance
    """
    plot_group = parser.add_argument_group(
        "Options specific to the plots you wish to make\n"
        "----------------------------------------------"
    )
    plot_group.add_argument(
        "--custom_plotting", dest="custom_plotting", default=None,
        help="Python file containing functions for custom plotting"
    )
    plot_group.add_argument(
        "--publication", action="store_true", default=None, help=(
            "generate production quality plots"
        )
    )
    plot_group.add_argument(
        "--publication_kwargs", action=DictionaryAction, nargs="+", default={},
        help="Optional kwargs for publication plots",
    )
    plot_group.add_argument(
        "--kde_plot", action="store_true", default=False, help=(
            "plot a kde rather than a histogram"
        )
    )
    plot_group.add_argument(
        "--colors", dest="colors", nargs='+', default=None,
        help="Colors you wish to use to distinguish result files",
    )
    plot_group.add_argument(
        "--palette", dest="palette", default="colorblind",
        help="Color palette to use to distinguish result files",
    )
    plot_group.add_argument(
        "--linestyles", dest="linestyles", nargs='+', default=None,
        help="Linestyles you wish to use to distinguish result files"
    )
    plot_group.add_argument(
        "--include_prior", action="store_true", default=False,
        help="Plot the prior on the same plot as the posterior",
    )
    plot_group.add_argument(
        "--style_file", dest="style_file", default=None,
        action=CheckFilesExistAction, help=(
            "Style file you wish to use when generating plots"
        )
    )
    plot_group.add_argument(
        "--add_to_corner", dest="add_to_corner", default=None,
        nargs="+", help="Parameters you wish to include in the corner plot"
    )
    plot_group.add_argument(
        "--add_existing_plot", dest="existing_plot", nargs="+", default=None,
        action=DictionaryAction, help=(
            "Path(s) to existing plots that you wish to add to the "
            "summarypages. Should be of the form {label}:{path}"
        )
    )
    return plot_group


def _webpage_command_line_arguments(parser):
    """Add specific command line options for the webpage generation

    Parameters
    ----------
    parser: object
        OptionParser instance
    """
    webpage_group = parser.add_argument_group(
        "Options specific to the webpages you wish to produce\n"
        "----------------------------------------------------"
    )
    webpage_group.add_argument(
        "--dump", action="store_true", default=False,
        help="dump all information onto a single html page",
    )
    webpage_group.add_argument(
        "--notes", dest="notes", default=None,
        help="Single file containing notes that you wish to put on summarypages"
    )
    return webpage_group


def _prior_command_line_arguments(parser):
    """Add specific command line options for prior files

    Parameters
    ----------
    parser: object
        OptionParser instance
    """
    prior_group = parser.add_argument_group(
        "Options specific for passing prior files\n"
        "----------------------------------------"
    )
    prior_group.add_argument(
        "--prior_file", dest="prior_file", nargs='+', default=None,
        action=CheckFilesExistAction, help=(
            "File containing for the prior samples for a given label"
        )
    )
    prior_group.add_argument(
        "--nsamples_for_prior", dest="nsamples_for_prior", default=5000,
        type=int, help=(
            "The number of prior samples to extract from a bilby prior file "
            "or a bilby result file"
        )
    )
    prior_group.add_argument(
        "--disable_prior_sampling", action="store_true",
        help="Skip generating prior samples using bilby", default=False
    )
    return prior_group


def _performance_command_line_options(parser):
    """Add command line options which enhance the performance of the code

    Parameters
    ----------
    parser: object
        OptionParser instance
    """
    performance_group = parser.add_argument_group(
        "Options specific for enhancing the performance of the code\n"
        "----------------------------------------------------------"
    )
    performance_group.add_argument(
        "--disable_comparison", action="store_true", default=False,
        help=(
            "Whether to make a comparison webpage if multple results are "
            "present"
        )
    )
    performance_group.add_argument(
        "--disable_interactive", action="store_true", default=False,
        help="Whether to make interactive plots or not"
    )
    performance_group.add_argument(
        "--disable_corner", action="store_true", default=False,
        help="Whether to make a corner plot or not"
    )
    performance_group.add_argument(
        "--disable_expert", action="store_true", default=False,
        help="Whether to generate extra diagnostic plots or not"
    )
    performance_group.add_argument(
        "--multi_process", dest="multi_process", default=1,
        help="The number of cores to use when generating plots"
    )
    performance_group.add_argument(
        "--file_format", dest="file_format", nargs='+', default=None,
        help="The file format of each result file."
    )
    performance_group.add_argument(
        "--restart_from_checkpoint", action="store_true", default=False,
        help=(
            "Restart from checkpoint if a checkpoint file can be found in "
            "webdir"
        )
    )
    return performance_group


def _pesummary_metafile_command_line_options(parser):
    """Add command line options which are specific for reading and
    manipulating pesummary metafiles

    Parameters
    ----------
    parser: object
        OptionParser instance
    """
    pesummary_group = parser.add_argument_group(
        "Options specific for reading and manipulating pesummary metafiles\n"
        "-----------------------------------------------------------------"
    )
    pesummary_group.add_argument(
        "--compare_results", dest="compare_results", nargs='+', default=None,
        help=(
            "labels for events stored in the posterior_samples.json that you "
            "wish to compare"
        )
    )
    pesummary_group.add_argument(
        "--save_to_json", action="store_true", default=False,
        help="save the meta file in json format"
    )
    pesummary_group.add_argument(
        "--posterior_samples_filename", dest="filename", default=None,
        help="name of the posterior samples metafile that is produced"
    )
    pesummary_group.add_argument(
        "--external_hdf5_links", action="store_true", default=False,
        help=(
            "save each analysis as a seperate hdf5 file and connect them to "
            "the meta file through external links"
        )
    )
    pesummary_group.add_argument(
        "--hdf5_compression", dest="hdf5_compression", default=None, type=int,
        help=(
            "compress each dataset with a particular compression filter. "
            "Filter must be integer between 0 and 9. Only applies to meta "
            "files stored in hdf5 format. Default, no compression applied"
        )
    )
    pesummary_group.add_argument(
        "--disable_injection", action="store_true", default=False,
        help=(
            "whether or not to extract stored injection data from the meta file"
        )
    )
    return pesummary_group


def command_line():
    """Generate an Argument Parser object to control the command line options
    """
    parser = argparse.ArgumentParser(description=__doc__)
    core_group = _core_command_line_arguments(parser)
    sample_group = _samples_command_line_arguments(parser)
    plot_group = _plotting_command_line_arguments(parser)
    webpage_group = _webpage_command_line_arguments(parser)
    prior_group = _prior_command_line_arguments(parser)
    performance_group = _performance_command_line_options(parser)
    pesummary_group = _pesummary_metafile_command_line_options(parser)
    return parser