# Copyright (C) 2018  Charlie Hoy <charlie.hoy@ligo.org> This program is free
# software; you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from pesummary import conf
from astropy import cosmology as cosmo

_available_cosmologies = cosmo.parameters.available + ["Planck15_lal"]
_available_cosmologies += [
    _cosmology + "_with_Riess2019_H0" for _cosmology in _available_cosmologies
]
available_cosmologies = [i.lower() for i in _available_cosmologies]


def get_cosmology(cosmology=conf.cosmology):
    """Return the cosmology that is being used

    Parameters
    ----------
    cosmology: str
        name of a known cosmology
    """
    if cosmology.lower() not in [i.lower() for i in available_cosmologies]:
        raise ValueError(
            "Unrecognised cosmology {}. Available cosmologies are {}".format(
                cosmology, ", ".join(available_cosmologies)
            )
        )
    if cosmology.lower() in [astropy.lower() for astropy in cosmo.__dict__.keys()]:
        if cosmology in cosmo.__dict__.keys():
            return cosmo.__dict__[cosmology]
        name = [
            astropy for astropy in cosmo.__dict__.keys() if
            astropy.lower() == cosmology
        ][0]
        return cosmo.__dict__[name]
    elif cosmology.lower() == "planck15_lal":
        return Planck15_lal_cosmology()
    elif "_with_riess2019_h0" in cosmology.lower():
        base_cosmology = cosmology.lower().split("_with_riess2019_h0")[0]
        return Riess2019_H0_cosmology(base_cosmology)


def Planck15_lal_cosmology():
    """Return the Planck15 cosmology coded up in lalsuite
    """
    return cosmo.LambdaCDM(H0=67.90, Om0=0.3065, Ode0=0.6935)


def Riess2019_H0_cosmology(base_cosmology):
    """Return the base cosmology but with the Riess2019 H0 value. For details
    see https://arxiv.org/pdf/1903.07603.pdf.

    Parameters
    ----------
    base_cosmology: str
        name of cosmology to use as the base
    """
    _base_cosmology = get_cosmology(base_cosmology)
    return cosmo.LambdaCDM(
        H0=74.03, Om0=_base_cosmology.Om0, Ode0=_base_cosmology.Ode0
    )
