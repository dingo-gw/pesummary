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

import copy

import argparse
import configparser


class ConfigAction(argparse.Action):
    """Class to extend the argparse.Action to handle dictionaries as input
    """
    def __init__(self, option_strings, dest, nargs=None, const=None,
                 default=None, type=None, choices=None, required=False,
                 help=None, metavar=None):
        super(ConfigAction, self).__init__(
            option_strings=option_strings, dest=dest, nargs=nargs,
            const=const, default=default, type=str, choices=choices,
            required=required, help=help, metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

        items = {}
        config = configparser.ConfigParser()
        try:
            config.read(values)
            for key, value in config.items("pesummary"):
                if value == "True" or value == "true":
                    items[key] = True
                else:
                    if ":" in value:
                        items[key] = self.dict_from_str(value)
                    elif "," in value:
                        items[key] = self.list_from_str(value)
                    else:
                        items[key] = value
        except Exception:
            pass
        for i in vars(namespace).keys():
            if i in items.keys():
                setattr(namespace, i, items[i])

    @staticmethod
    def dict_from_str(string):
        """Reformat the string into a dictionary

        Parameters
        ----------
        string: str
            string that you would like reformatted into a dictionary
        """
        mydict = {}
        if "{" in string:
            string.replace("{", "")
        if "}" in string:
            string.replace("}", "")
        if " " in string and ": " not in string:
            string = string.split(" ")
        elif "," in string:
            string = string.split(",")
        for i in string:
            value = i.split(":")
            if " " in value[0]:
                value[0] = value[0].replace(" ", "")
            if " " in value[1]:
                value[1] = value[1].replace(" ", "")
            if value[0] in mydict.keys():
                mydict[value[0]].append(value[1])
            else:
                mydict[value[0]] = [value[1]]
        return mydict

    @staticmethod
    def list_from_str(string):
        """Reformat the string into a list

        Parameters
        ----------
        string: str
            string that you would like reformatted into a list
        """
        list = []
        if "[" in string:
            string.replace("[", "")
        if "]" in string:
            string.replace("]", "")
        if ", " in string:
            list = string.split(", ")
        elif " " in string:
            list = string.split(" ")
        elif "," in string:
            list = string.split(",")
        return list


def command_line():
    """Generate an Argument Parser object to control the command line options
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pesummary", nargs='?', help=(
                        "configuration file containing the command line "
                        "arguments"), action=ConfigAction)
    parser.add_argument("-w", "--webdir", dest="webdir",
                        help="make page and plots in DIR", metavar="DIR",
                        default=None)
    parser.add_argument("-b", "--baseurl", dest="baseurl",
                        help="make the page at this url", metavar="DIR",
                        default=None)
    parser.add_argument("-s", "--samples", dest="samples",
                        help="Posterior samples hdf5 file", nargs='+',
                        default=None)
    parser.add_argument("-c", "--config", dest="config",
                        help=("configuration file associcated with "
                              "each samples file."),
                        nargs='+', default=None)
    parser.add_argument("--email", action="store",
                        help=("send an e-mail to the given address with a link "
                              "to the finished page."), default=None)
    parser.add_argument("--dump", action="store_true",
                        help="dump all information onto a single html page",
                        default=False)
    parser.add_argument("--add_to_existing", action="store_true",
                        help="add new results to an existing html page",
                        default=False)
    parser.add_argument("-e", "--existing_webdir", dest="existing",
                        help="web directory of existing output", default=None)
    parser.add_argument("-i", "--inj_file", dest="inj_file",
                        help="path to injetcion file", nargs='+', default=None)
    parser.add_argument("--user", dest="user", help=argparse.SUPPRESS,
                        default="albert.einstein")
    parser.add_argument("--labels", dest="labels",
                        help="labels used to distinguish runs", nargs='+',
                        default=None)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print useful information for debugging purposes")
    parser.add_argument("--save_to_hdf5", action="store_true",
                        help="save the meta file in hdf5 format", default=False)
    return parser