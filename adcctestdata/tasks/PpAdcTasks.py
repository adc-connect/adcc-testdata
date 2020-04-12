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
from .MpTasks import TaskHf, TaskMp1, TaskMp2Td2
from .AdcCommon import AdcCommon
from .OtherTasks import TaskDysonExpansionMethod

from pyadcman import CtxMap

# Documentation for the parameters:
#   adcman/adcman/qchem/params_reader.h
#   adcman/adcman/qchem/params_reader.C


# Part of the functions used here, are implemented in AdcCommon

class AdcTaskBase(AdcCommon):
    adcclass = "pp"

    @classmethod
    def adc_level(cls):
        if cls.name == "adc0":
            return 0
        if cls.name == "adc1":
            return 1
        if cls.name in ["adc2", "adc2x"]:
            return 2
        if cls.name == "adc3":
            return 3
        else:
            raise ValueError("Level cannot be determined for method " + cls.name)

    @classmethod
    def parameters(cls, **kwargs):
        adc_variant = kwargs.get("adc_variant", [])

        # Determine the variant string
        variant = cls.name
        if variant == "adc2":
            variant = "adc2s"
        if "ri" in adc_variant:
            variant = "ri_" + variant
        if "sos" in adc_variant:
            variant = "sos_" + variant
        if "cvs" in adc_variant:
            variant = "cvs_" + variant

        params = CtxMap({"adc_pp": "1"})
        params["adc_pp/" + variant] = "1"
        cls.add_common_adc_params_to(params.submap("adc_pp/" + variant), **kwargs)
        return params

    @classmethod
    def add_common_adc_params_to(cls, tadc, restricted=False, n_singlets=0,
                                 n_triplets=0, n_states=0,
                                 ground_state_density=None, **kwargs):
        adc_variant = kwargs.get("adc_variant", [])
        cls.insert_print_subtree(tadc, **kwargs)

        # Insert intermediates for appropriate ADC level
        tadc["prereq/adc{}_im".format(cls.adc_level())] = "1"

        # Insert iterated density:
        if cls.adc_level() <= 2:
            if ground_state_density is not None:
                raise ValueError(f"Explicit selection of ground state density "
                                 "order not compatible with "
                                 f"ADC{cls.adc_level()}")
        elif ground_state_density is None or ground_state_density == "mp2":
            tadc["prereq/iterated_density"] = "0"
            tadc["prereq/third_order_density"] = "0"
        elif ground_state_density == "mp3":
            tadc["prereq/iterated_density"] = "0"
            tadc["prereq/third_order_density"] = "1"
        elif ground_state_density == "dyson":
            tadc["prereq/iterated_density"] = "1"
            tadc["prereq/third_order_density"] = "0"
        else:
            raise ValueError(f"ground_state_density == {ground_state_density} "
                             "not implemented for ADC(3)")

        # Build restricted / unrestricted subtree
        if restricted:
            if "sf" in adc_variant:
                raise ValueError("Cannot run spin-flip for restricted "
                                 "references.")
            if n_states > 0:
                raise ValueError("Cannot use n_states for restricted references.")
            if n_singlets + n_triplets == 0:
                raise ValueError("n_singlets + n_triplets needs to be larger 0 "
                                 "for restricted references.")

            tadc["rhf"] = "1"
            tadc["uhf"] = "0"
            if n_singlets > 0:
                tadc["rhf/singlets"] = "1"
                cls.add_state_params_to(tadc.submap("rhf/singlets"), "singlet",
                                        n_singlets, **kwargs)
                cls.add_state2state_params_to(tadc.submap("rhf/singlets"),
                                              "singlet", n_singlets,
                                              n_singlets, **kwargs)
            else:
                tadc["rhf/singlets"] = "0"

            if n_triplets > 0:
                tadc["rhf/triplets"] = "1"
                cls.add_state_params_to(tadc.submap("rhf/triplets"), "triplet",
                                        n_triplets, **kwargs)
                cls.add_state2state_params_to(tadc.submap("rhf/triplets"),
                                              "triplet", n_triplets,
                                              n_triplets, **kwargs)
            else:
                tadc["rhf/triplets"] = "0"

            if n_singlets > 0 and n_triplets > 0:
                # Singlet 2 triplet properties
                cls.add_state2state_params_to(tadc.submap("rhf"), "s2t",
                                              n_singlets, n_triplets, **kwargs)
        else:
            if n_singlets > 0 or n_triplets > 0:
                raise ValueError("Cannot use n_singlets or n_triplets for "
                                 "unrestricted references.")
            if n_states == 0:
                raise ValueError("n_states needs to be larger 0 for unrestricted "
                                 "references.")

            tadc["rhf"] = "0"
            tadc["uhf"] = "1"
            cls.add_state_params_to(tadc.submap("uhf"), "any", n_states, **kwargs)
            cls.add_state2state_params_to(tadc.submap("uhf"), "any", n_states,
                                          n_states, **kwargs)


class TaskAdc0(AdcTaskBase):
    dependencies = [TaskHf]
    name = "adc0"


class TaskAdc1(AdcTaskBase):
    dependencies = [TaskMp1]
    name = "adc1"


class TaskAdc2(AdcTaskBase):
    dependencies = [TaskMp2Td2]
    name = "adc2"


class TaskAdc2x(AdcTaskBase):
    dependencies = [TaskMp2Td2]
    name = "adc2x"


class TaskAdc3(AdcTaskBase):
    dependencies = [TaskDysonExpansionMethod]
    name = "adc3"
