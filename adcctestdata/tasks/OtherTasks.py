#!/usr/bin/env python3
## vi: tabstop=4 shiftwidth=4 softtabstop=4 expandtab
## ---------------------------------------------------------------------
##
## Copyright (C) 2019 by Michael F. Herbst
##
## This file is part of adcc-testdata.
##
## adcc-testdata is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published
## by the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## adcc-testdata is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with adcc-testdata. If not, see <http://www.gnu.org/licenses/>.
##
## ---------------------------------------------------------------------
from .MpTasks import TaskMp1, TaskMp3

from pyadcman import CtxMap


class TaskPia:
    """
    Computes the following objects into the context
      - The Pia N^6 intermediates
           /gen/prereq/pia_o1o1o1v1
    """
    dependencies = [TaskMp1]
    name = "pia"

    @classmethod
    def parameters(cls, **kwargs):
        return CtxMap({"gen_prereq/pia": "1"})


class TaskPib:
    """
    Computes the following objects into the context
      - The Pia N^6 intermediates
           /gen/prereq/pib_o1v1v1v1
    """
    dependencies = [TaskMp1]
    name = "pib"

    @classmethod
    def parameters(cls, **kwargs):
        return CtxMap({"gen_prereq/pib": "1"})


class TaskDysonExpansionMethod:
    # Computes MP3 density or higher-order density via dyson-expansion method
    dependencies = [TaskMp3, TaskPia, TaskPib]
    name = "dyson_expansion_method"

    @classmethod
    def parameters(cls, ground_state_density=None, **kwargs):
        if ground_state_density is None or ground_state_density == "mp2":
            return CtxMap()  # No work needed here
        elif ground_state_density not in ["mp3", "dyson"]:
            raise ValueError(f"Unrecognised value for "
                             "ground_state_density: {ground_state_density}")

        adc_variant = kwargs.get("adc_variant", [])
        if adc_variant != []:
            raise ValueError("Right now Dyson-expansion method only works for "
                             "ADC without special variants.")

        params = CtxMap({"iterated_density": "1"})
        tdem = params.submap("iterated_density")

        # Choose some hard-coded parameters for the density iterations
        tdem["direct"] = "1"
        tdem["convergence"] = str(kwargs.get("conv_tol", 1e-6) / 100)
        tdem["maxiter"] = "1000"
        # TODO Also needs m_n6_prereq_im.insert("oovv");

        if ground_state_density == "mp3":
            tdem["order"] = "3"
        else:
            tdem["order"] = "3+"
        return params
