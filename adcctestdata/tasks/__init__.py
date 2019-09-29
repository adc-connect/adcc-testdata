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
from . import MpTasks, PiTasks

__all__ = ["parameters"]


def resolve_method(method):
    for module in [MpTasks, PiTasks]:
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


def parameters(method, print_level=0, **kwargs):
    """
    Return the parameter tree required for running the passed
    method under the passed parameters. Method should be a string.
    """
    # TODO update, because sometimes base method is not equal to
    #      method (e.g. cvs)
    basemethod = method

    task = resolve_method(basemethod)
    params = collect_task_parameters(task, **kwargs)

    # TODO Sometimes we need to set extra stuff,
    #      e.g. the core parameter in core-valence separation.

    # Keys required for sucessful execution
    if "prop" not in params.get("hf", {}):
        params["hf/prop"] = "0"  # False
    if "prop" not in params.get("mp2", {}):
        params["mp2/prop"] = "0"  # False

    params["print_level"] = str(print_level)
    return params
