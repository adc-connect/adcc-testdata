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


class AdcCommon:
    @classmethod
    def insert_print_subtree(cls, tree, print_level=1, adc_variant=[], **kwargs):
        tree["print/print_level"] = str(print_level)

        nampl = 0
        if print_level >= 1:
            nampl = 2
        elif print_level >= 2:
            nampl = 20
        elif print_level >= 3:
            nampl = 40
        else:
            nampl = 60
        tree["print/nampl"] = str(nampl)

        # No PCM at the moment
        tree["print/pcm"] = "0"  # False
        tree["print/cvs"] = "0"
        tree["print/sf"] = "0"
        if "cvs" in adc_variant:
            tree["print/cvs"] = "1"
        if "sf" in adc_variant:
            tree["print/sf"] = "1"

        return tree

    @classmethod
    def add_state_params_to(cls, tspin, spin, n_states, **kwargs):
        """
        Add the unrestr_alpha/unrestr_beta/restr_beta parameters to `tspin`, where
        `spin` is "unrestr_alpha", "unrestr_beta" or "restr_beta" and n_states is
        the number of states to be computed.
        """
        # TODO This assumes only a single irrep
        irrep = "0"
        tspin[irrep] = "1"  # enable irrep
        cls.add_state_irrep_params_to(tspin.submap(irrep), spin, irrep,
                                      n_states, **kwargs)

    @classmethod
    def add_state_irrep_params_to(cls, tirrep, spin, irrep, n_states,
                                  adc_variant=[], **kwargs):
        """
        Add the subtree data for a particular irrep. Adds keys like:
          - solver
          - spin
          - ...

        `tirrep` is the subtree for this irrep, `spin` is "singlet", "triplet"
        or "any",`n_states` is the number of states of this irrep to be computed
        """
        # Setup spin-related things
        tirrep["spin"] = spin
        tirrep["irrep"] = irrep
        tirrep["nroots"] = str(n_states)

        # Special stuff for PP methods:
        if cls.adcclass == "pp":
            # Force using the ADC(3) method, which requires precomputation
            # of pib intermediates
            tirrep["direct"] = "0"

            # Set spin-flip if needed
            tirrep["spin_flip"] = "0"
            if "sf" in adc_variant:
                tirrep["spin_flip"] = "1"

        # All adcclasses have state properties ...
        propkeys = ["prop"]
        tirrep["opdm"] = "1"  # One-particle density matrix
        if cls.adcclass == "pp":
            # ... PP also has ground -> state transition properties
            tirrep["optdm"] = "1"
            propkeys.append("tprop")  # One-particle transition density matrix
        for pt in propkeys:
            tirrep[pt + "/."] = "1"
            tirrep[pt + "/dipole"] = "1"
            tirrep[pt + "/rsq"] = "0"

        # Setup solver-related parameters inside the subtree
        cls.add_solver_params_to(tirrep, n_states, **kwargs)

    @classmethod
    def add_solver_params_to(cls, tirrep, n_states, solver="davidson",
                             conv_tol=1e-6, residual_min_norm=1e-12, max_iter=0,
                             max_subspace=60, **kwargs):
        """
        Add parameters for one particular davidson solver run to the
        (irrep-specific) parameter tree. `n_states` is the number of states to
        compute in this very irrep. Includes keys like:
          - guesses
          - solver
          - davidson
          - ...
        """
        # Setup guesses
        if cls.adcclass == "pp":
            guessmap = {"s": ("nguess_singles", "n_guess_singles"),
                        "d": ("nguess_doubles", "n_guess_doubles"), }
        elif cls.adcclass == "ip":
            guessmap = {"s": ("nguess_h", "n_guess_h"),
                        "d": ("nguess_p2h", "n_guess_p2h"), }
        else:
            raise NotImplementedError(f"adcclass {cls.adcclass} not implemented.")

        tirrep[guessmap["s"][0]] = str(kwargs[guessmap["s"][1]])
        tirrep[guessmap["d"][0]] = str(kwargs[guessmap["d"][1]])
        sum_guesses = kwargs[guessmap["s"][1]] + kwargs[guessmap["d"][1]]
        if sum_guesses < n_states:
            tirrep[guessmap["s"][0]] = str(n_states - kwargs[guessmap["d"][1]])

        # Set solver parameters
        tirrep["solver"] = solver
        tirrep[solver + "/convergence"] = str(conv_tol)
        tirrep[solver + "/maxiter"] = str(max_iter)
        tirrep[solver + "/threshold"] = str(residual_min_norm)

        # Special adjustment for davidson
        if solver == "davidson":
            if max_subspace == 0:
                max_subspace = 5 * n_states
            elif max_subspace < n_states:
                max_subspace = 2 * n_states
            tirrep["davidson/maxsubspace"] = str(max_subspace)

    @classmethod
    def add_state2state_params_to(cls, tspin, spin, n_states1, n_states2,
                                  **kwargs):
        """
        Parameters for state2state properties
        """
        tspin["isr"] = "1"
        irrep1 = irrep2 = "0"  # TODO Assume only one irrep

        tirrep = tspin.submap("isr/" + irrep1 + "-" + irrep2)
        tirrep["."] = "1"      # Enable state2state for irrep
        tirrep["optdm"] = "1"  # Transition density matrices
        tirrep["tprop"] = "1"  # Transition properties

        if spin in ["s2t", "any"]:
            # Spin-orbit coupling
            tirrep["tprop/soc"] = "0"
        if spin != "s2t":
            tirrep["tprop/dipole"] = "1"
            tirrep["tprop/rsq"] = "0"
