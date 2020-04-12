#!/usr/bin/env python3
## vi: tabstop=4 shiftwidth=4 softtabstop=4 expandtab
## ---------------------------------------------------------------------
##
## Copyright (C) 2020 by Michael F. Herbst
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
from .MpTasks import TaskHf, TaskMp2
from .AdcCommon import AdcCommon
from .OtherTasks import TaskDysonExpansionMethod

from pyadcman import CtxMap

# Documentation for the parameters:
#   adcman/adcman/qchem/params_reader.h
#   adcman/adcman/qchem/params_reader.C


# Part of the functions used here, are implemented in AdcCommon

class IpAdcTaskBase(AdcCommon):
    adcclass = "ip"

    @classmethod
    def adc_level(cls):
        if cls.name == "ipadc0":
            return 0
        if cls.name == "ipadc2":
            return 2
        if cls.name == "ipadc3":
            return 3
        else:
            raise ValueError("Level cannot be determined for method " + cls.name)

    @classmethod
    def parameters(cls, **kwargs):
        adc_variant = kwargs.get("adc_variant", [])
        if adc_variant:
            raise ValueError("Right now IP-ADC has no variants implemented.")

        # Determine the variant string
        assert cls.name[0:2] == "ip"
        variant = cls.name[2:]
        # TODO Stuff in PP adc tree
        # if "ri" in adc_variant:
        #     variant = "ri_" + variant
        # if "sos" in adc_variant:
        #     variant = "sos_" + variant
        # if "cvs" in adc_variant:
        #     variant = "cvs_" + variant

        params = CtxMap({"adc_ip": "1"})
        params["adc_ip/" + variant] = "1"
        cls.add_common_adc_params_to(params.submap("adc_ip/" + variant), **kwargs)
        return params

    @classmethod
    def add_common_adc_params_to(cls, tadc, restricted=False, n_ipalpha=0,
                                 n_ipbeta=0, ground_state_density=None,
                                 **kwargs):
        cls.insert_print_subtree(tadc, **kwargs)

        # Purge n_states parameter if it's still in the kwargs
        kwargs.pop("n_states", None)

        # Insert intermediates for appropriate ADC level
        tadc["prereq/adc{}_im".format(cls.adc_level())] = "1"

        # Insert effective transition moments
        if cls.adc_level() <= 2:
            if ground_state_density is not None:
                raise ValueError(f"Explicit selection of ground state density "
                                 "order not compatible with "
                                 f"IP-ADC{cls.adc_level()}")
            tadc["prereq/adc{}_etm".format(cls.adc_level())] = "1"
        elif ground_state_density is None or ground_state_density == "mp2":
            tadc["prereq/adc3_etm"] = "2"
        elif ground_state_density == "mp3":
            tadc["prereq/adc3_etm"] = "3"
        elif ground_state_density == "dyson":
            tadc["prereq/adc3_etm"] = "3+"
        else:
            raise ValueError(f"ground_state_density == {ground_state_density} "
                             "not implemented for IP-ADC(3)")

        # Build restricted / unrestricted subtree
        if restricted:
            if n_ipalpha > 0:
                raise ValueError("Adcman only computes beta ionisations "
                                 "for restricted references.")

            tadc["rhf"] = "1"
            tadc["uhf"] = "0"
            cls.add_state_params_to(tadc.submap("rhf"), "restr_beta",
                                    n_ipbeta, **kwargs)
            cls.add_state2state_params_to(tadc.submap("rhf"), "restr_beta",
                                          n_ipbeta, n_ipbeta, **kwargs)
        else:
            tadc["rhf"] = "0"
            tadc["uhf"] = "1"
            if n_ipalpha > 0:
                tadc["uhf/alphas"] = "1"
                cls.add_state_params_to(tadc.submap("uhf/alphas"),
                                        "unrestr_alpha", n_ipalpha, **kwargs)
                cls.add_state2state_params_to(tadc.submap("uhf/alphas"),
                                              "unrestr_alpha", n_ipalpha,
                                              n_ipalpha, **kwargs)
            if n_ipbeta > 0:
                tadc["uhf/betas"] = "1"
                cls.add_state_params_to(tadc.submap("uhf/betas"), "unrestr_beta",
                                        n_ipbeta, **kwargs)
                cls.add_state2state_params_to(tadc.submap("uhf/betas"),
                                              "unrestr_beta", n_ipbeta,
                                              n_ipbeta, **kwargs)


class TaskIpAdc0(IpAdcTaskBase):
    dependencies = [TaskHf]
    name = "ipadc0"


class TaskIpAdc2(IpAdcTaskBase):
    dependencies = [TaskMp2]
    name = "ipadc2"


class TaskIpAdc3(IpAdcTaskBase):
    dependencies = [TaskDysonExpansionMethod]
    name = "ipadc3"
