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


standard_names = {"logL": "log_likelihood",
                  "logl": "log_likelihood",
                  "lnL": "log_likelihood",
                  "log_likelihood": "log_likelihood",
                  "tilt1": "tilt_1",
                  "tilt_1": "tilt_1",
                  "tilt_spin1": "tilt_1",
                  "theta_1l": "tilt_1",
                  "tilt2": "tilt_2",
                  "tilt_2": "tilt_2",
                  "tilt_spin2": "tilt_2",
                  "theta_2l": "tilt_2",
                  "costilt1": "cos_tilt_1",
                  "costilt2": "cos_tilt_2",
                  "redshift": "redshift",
                  "l1_optimal_snr": "L1_optimal_snr",
                  "h1_optimal_snr": "H1_optimal_snr",
                  "v1_optimal_snr": "V1_optimal_snr",
                  "L1_optimal_snr": "L1_optimal_snr",
                  "H1_optimal_snr": "H1_optimal_snr",
                  "V1_optimal_snr": "V1_optimal_snr",
                  "E1_optimal_snr": "E1_optimal_snr",
                  "l1_matched_filter_snr": "L1_matched_filter_snr",
                  "h1_matched_filter_snr": "H1_matched_filter_snr",
                  "v1_matched_filter_snr": "V1_matched_filter_snr",
                  "L1_matched_filter_snr": "L1_matched_filter_snr",
                  "H1_matched_filter_snr": "H1_matched_filter_snr",
                  "V1_matched_filter_snr": "V1_matched_filter_snr",
                  "E1_matched_filter_snr": "E1_matched_filter_snr",
                  "mc_source": "chirp_mass_source",
                  "chirpmass_source": "chirp_mass_source",
                  "chirp_mass_source": "chirp_mass_source",
                  "eta": "symmetric_mass_ratio",
                  "symmetric_mass_ratio": "symmetric_mass_ratio",
                  "m1": "mass_1",
                  "mass_1": "mass_1",
                  "m2": "mass_2",
                  "mass_2": "mass_2",
                  "ra": "ra",
                  "rightascension": "ra",
                  "dec": "dec",
                  "declination": "dec",
                  "iota": "iota",
                  "incl": "iota",
                  "m2_source": "mass_2_source",
                  "mass_2_source": "mass_2_source",
                  "m1_source": "mass_1_source",
                  "mass_1_source": "mass_1_source",
                  "phi1": "phi_1",
                  "phi_1l": "phi_1",
                  "phi_1": "phi_1",
                  "phi2": "phi_2",
                  "phi_2l": "phi_2",
                  "phi_2": "phi_2",
                  "psi": "psi",
                  "polarisation": "psi",
                  "phi12": "phi_12",
                  "phi_12": "phi_12",
                  "phi_jl": "phi_jl",
                  "phijl": "phi_jl",
                  "a1": "a_1",
                  "a_1": "a_1",
                  "a_spin1": "a_1",
                  "spin1": "a_1",
                  "a1x": "spin_1x",
                  "a1y": "spin_1y",
                  "a1z": "spin_1z",
                  "spin_1x": "spin_1x",
                  "spin_1y": "spin_1y",
                  "spin_1z": "spin_1z",
                  "a2": "a_2",
                  "a_2": "a_2",
                  "a_spin2": "a_2",
                  "spin2": "a_2",
                  "a2x": "spin_2x",
                  "a2y": "spin_2y",
                  "a2z": "spin_2z",
                  "spin_2x": "spin_2x",
                  "spin_2y": "spin_2y",
                  "spin_2z": "spin_2z",
                  "chi_p": "chi_p",
                  "phase": "phase",
                  "phiorb": "phase",
                  "phi0": "phase",
                  "phiorb": "phase",
                  "phi0": "phase",
                  "distance": "luminosity_distance",
                  "dist": "luminosity_distance",
                  "luminosity_distance": "luminosity_distance",
                  "mc": "chirp_mass",
                  "chirpmass": "chirp_mass",
                  "chirp_mass": "chirp_mass",
                  "chi_eff": "chi_eff",
                  "mtotal_source": "total_mass_source",
                  "total_mass_source": "total_mass_source",
                  "mtotal": "total_mass",
                  "total_mass": "total_mass",
                  "q": "mass_ratio",
                  "mass_ratio": "mass_ratio",
                  "time": "geocent_time",
                  "tc": "geocent_time",
                  "geocent_time": "geocent_time",
                  "theta_jn": "theta_jn",
                  "reference_frequency": "reference_frequency",
                  "fref": "reference_frequency",
                  "time_maxl": "marginalized_geocent_time",
                  "phase_maxl": "marginalized_phase",
                  "distance_maxl": "marginalized_distance"}
