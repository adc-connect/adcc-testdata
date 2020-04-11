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

__all__ = ["parameters"]


def resolve_method(method):
    from . import AdcTasks, IpAdcTasks, MpTasks, OtherTasks

    for module in [MpTasks, OtherTasks, AdcTasks, IpAdcTasks]:
        for clsstr in dir(module):
            if not clsstr.startswith("Task"):
                continue
            cls = getattr(module, clsstr)
            if hasattr(cls, "name") and cls.name == method:
                return cls
    raise ValueError("Unknown method string: {}".format(method))


def collect_task_parameters(task, **kwargs):
    """
    Collect the parameters required to run the task and recursively
    the parameters for all of the tasks' dependencies.
    """
    ret = task.parameters(**kwargs)
    for dep in task.dependencies:
        ret.update(collect_task_parameters(dep, **kwargs))
    return ret


def parameters(basemethod, adc_variant, print_level=0, **kwargs):
    """
    Return the parameter tree required for running the passed
    method under the passed parameters. Method should be a string.
    """
    task = resolve_method(basemethod)
    params = collect_task_parameters(task, adc_variant=adc_variant,
                                     print_level=print_level, **kwargs)

    params["print_level"] = str(print_level)
    if "cvs" in adc_variant:
        params["core"] = "1"  # Enable CVS
    return params
