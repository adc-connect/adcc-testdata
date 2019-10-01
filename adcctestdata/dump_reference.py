#!/usr/bin/env python3
## vi: tabstop=4 shiftwidth=4 softtabstop=4 expandtab
## ---------------------------------------------------------------------
##
## Copyright (C) 2019 by Michael F. Herbst
##
## This file is part of adcc-testdata.
##
## adcc-testdata is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published
## by the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## adcc-testdata is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with adcc-testdata. If not, see <http://www.gnu.org/licenses/>.
##
## ---------------------------------------------------------------------
import numpy as np

from .run_adcman import run_adcman

import h5py


def dump_reference(data, method, dumpfile, mp_tree="mp", adc_tree="adc", n_states_full=None,
                   **kwargs):
    """
    Run a reference calculation and dump the computed data as an HDF5 file.
    All kwargs are passed to :py:`run_adcman`.

    Parameters
    ----------
    data : adcc.HdfProvider or h5py.File or str
        SCF data to run ADC upon

    method : str
        ADC method to execute

    dumpfile : str
        HDF5 file to employ for dumping the data

    mp_tree : str
        Name of the HDF5 group to store the MP results

    adc_tree : str
        Name of the HDF5 group to store the ADC results

    n_states_full : int or NoneType
        The number of states to include in full in the dump
        (i.e. including singles and doubles parts of the excitatation vectors)
    """
    ctx = run_adcman(data, method, **kwargs)

    if isinstance(dumpfile, h5py.File):
        out = dumpfile
    elif isinstance(dumpfile, str):
        out = h5py.File(dumpfile)
    else:
        raise TypeError("Unknown type for out, only HDF5 file and str supported.")

    # Tree where the ADC data is to be found
    method_tree = "adc_pp/" + method.replace("-", "_")
    if method in ["adc2", "cvs-adc2"]:
        method_tree += "s"

    #
    # MP
    #
    mp = out.create_group(mp_tree)

    if "mp2/energy" in ctx:
        mp["mp2/energy"] = ctx["/mp2/energy"]
    if "mp3/energy" in ctx and method != "cvs-adc3":
        # For CVS-ADC(3) the MP3 energy in adcman is wrong!
        mp["mp3/energy"] = ctx["/mp3/energy"]
    if "mp2/prop/dipole" in ctx:
        mp["mp2/dipole"] = np.array(ctx["/mp2/prop/dipole"])

    for key in ["mp1/t_o1o1v1v1", "mp1/t_o2o2v1v1", "mp1/t_o1o2v1v1",
                "mp1/df_o1v1", "mp1/df_o2v1", "mp2/td_o1o1v1v1"]:
        if key in ctx:
            mp.create_dataset(key, data=ctx[key].to_ndarray(),
                              compression=8)

    for block in ["dm_o1o1", "dm_o1v1", "dm_v1v1", "dm_bb_a", "dm_bb_b",
                  "dm_o2o1", "dm_o2o2", "dm_o2v1"]:
        if "mp2/opdm/" + block in ctx:
            mp.create_dataset("mp2/" + block, compression=8,
                              data=ctx["mp2/opdm/" + block].to_ndarray())

    #
    # ADC
    #
    adc = out.create_group(adc_tree)
    kind_trees = {
        "singlet": method_tree + "/rhf/singlets/0",
        "triplet": method_tree + "/rhf/triplets/0",
        "state": method_tree + "/uhf/0",
        "spin_flip": method_tree + "/uhf/0",
    }
    if "n_spin_flip" not in kwargs:
        del kind_trees["spin_flip"]
    if "n_states" not in kwargs:
        del kind_trees["state"]

    available_kinds = []
    for kind, tree in kind_trees.items():
        dm_bb_a = []
        dm_bb_b = []
        tdm_bb_a = []
        tdm_bb_b = []
        state_dipoles = []
        transition_dipoles = []
        eigenvalues = []
        eigenvectors_singles = []
        eigenvectors_doubles = []
        n_states = ctx.get(tree + "/nstates", 0)
        if n_states == 0:
            continue
        available_kinds.append(kind)

        # From 2 states we save everything
        if n_states_full is not None:
            n_states_extract = max(n_states_full, n_states)
        else:
            n_states_extract = n_states

        for i in range(n_states_extract):
            state_tree = tree + "/es" + str(i)

            dm_bb_a.append(ctx[state_tree + "/opdm/dm_bb_a"].to_ndarray())
            dm_bb_b.append(ctx[state_tree + "/opdm/dm_bb_b"].to_ndarray())
            tdm_bb_a.append(ctx[state_tree + "/optdm/dm_bb_a"].to_ndarray())
            tdm_bb_b.append(ctx[state_tree + "/optdm/dm_bb_b"].to_ndarray())

            state_dipoles.append(ctx[state_tree + "/prop/dipole"])
            transition_dipoles.append(ctx[state_tree + "/tprop/dipole"])

            eigenvalues.append(ctx[state_tree + "/energy"])
            eigenvectors_singles.append(
                ctx[state_tree + "/u1"].to_ndarray()
            )
            if state_tree + "/u2" in ctx:
                eigenvectors_doubles.append(
                    ctx[state_tree + "/u2"].to_ndarray()
                )
            else:
                eigenvectors_doubles.clear()

        # from the others only the energy and dipoles
        for i in range(n_states_extract, n_states):
            state_tree = tree + "/es" + str(i)
            state_dipoles.append(ctx[state_tree + "/prop/dipole"])
            transition_dipoles.append(ctx[state_tree + "/tprop/dipole"])
            eigenvalues.append(ctx[state_tree + "/energy"])

        # Transform to numpy array
        adc[kind + "/state_diffdm_bb_a"] = np.asarray(dm_bb_a)
        adc[kind + "/state_diffdm_bb_b"] = np.asarray(dm_bb_b)
        adc[kind + "/ground_to_excited_tdm_bb_a"] = np.asarray(tdm_bb_a)
        adc[kind + "/ground_to_excited_tdm_bb_b"] = np.asarray(tdm_bb_b)
        adc[kind + "/state_dipole_moments"] = np.asarray(state_dipoles)
        adc[kind + "/transition_dipole_moments"] = np.asarray(transition_dipoles)
        adc[kind + "/eigenvalues"] = np.array(eigenvalues)
        adc[kind + "/eigenvectors_singles"] = np.asarray(eigenvectors_singles)

        if eigenvectors_doubles:  # For ADC(0) and ADC(1) there are no doubles
            adc.create_dataset(kind + "/eigenvectors_doubles", compression=8,
                               data=np.asarray(eigenvectors_doubles))
    # for kind

    out.create_dataset("available_kinds", shape=(len(available_kinds), ),
                       data=np.array(available_kinds,
                                     dtype=h5py.special_dtype(vlen=str)))
    return out
