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
from pyadcman import CtxMap

# Documentation for the parameters:
#   adcman/adcman/qchem/params_reader.h
#   adcman/adcman/qchem/params_reader.C


class TaskHf:
    """
    Computes Hf properties into context.
    """
    dependencies = []
    name = "hf"

    @classmethod
    def parameters(cls, **kwargs):
        return CtxMap({
            "hf/prop": "1",
            "hf/prop/dipole": "1",
            "hf/prop/rsq": "0"
        })


class TaskMp1:
    """
    Computes these objects into the context:
        - Delta fock matrix
            /mp1/df_o1v1
        - MP t amplitudes
            /mp1/t_o1o1v1v1
    """
    dependencies = [TaskHf]
    name = "mp1"

    @classmethod
    def parameters(cls, **kwargs):
        return CtxMap({"mp1": "1"})  # "1" == true


class TaskMp2:
    """
    Computes the following objects into the context
      - The one-particle density matrices
           /mp2/opdm/dm_bb_a
        and related
      - The MP2 energy and the ground state energy at MP2 level
           /mp2/total_energy
           /mp2/energy
    """
    dependencies = [TaskMp1]
    name = "mp2"

    @classmethod
    def parameters(cls, **kwargs):
        return CtxMap({
            "mp2": "1",
            "mp2/opdm": "1",   # Note: This is always needed
            "mp2/prop": "1",
            "mp2/prop/dipole": "1",
            "mp2/prop/rsq": "0"
        })


class TaskPiOovv:
    """
    Computes the following objects into the context
      - The Pi3, Pi4, Pi5 N^6 intermediates
           /gen/prereq/pi3_o1o1v1v1
           /gen/prereq/pi4_o1o1v1v1
           /gen/prereq/pi5_o1o1v1v1
    """
    dependencies = [TaskMp1]
    name = "pi_oovv"

    @classmethod
    def parameters(cls, **kwargs):
        return CtxMap({
            "gen_prereq/pi3": "1",
            "gen_prereq/pi4": "1",
            "gen_prereq/pi5": "1",
        })


class TaskMp2Td2:
    """
    Computes the following objects into the context
      - The MP td amplitudes
           /mp2/td_o1o1v1v1
    """
    dependencies = [TaskMp2, TaskPiOovv]
    name = "mp2td2"

    @classmethod
    def parameters(cls, **kwargs):
        return CtxMap({"mp2/td2": "1"})


class TaskMp3:
    """
    Computes the following objects into the context
      - The MP3 energy and the ground state energy at MP3 level
           /mp3/total_energy
           /mp3/energy
    """
    dependencies = [TaskMp2Td2]
    name = "mp3"

    @classmethod
    def parameters(cls, **kwargs):
        return CtxMap({"mp3": "1"})
