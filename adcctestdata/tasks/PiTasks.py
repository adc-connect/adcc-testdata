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
from .MpTasks import TaskMp1
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
