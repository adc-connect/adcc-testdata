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
import h5py
import pyadcman

from . import tasks
from .HdfProvider import HdfProvider


def get_valid_methods():
    valid_prefixes = ["cvs"]
    valid_bases = ["adc0", "adc1", "adc2", "adc2x", "adc3",
                   "ipadc0", "ipadc2", "ipadc3"]

    ret = valid_bases + [p + "-" + m for p in valid_prefixes for m in valid_bases]
    return ret


def as_tensor_bb(mospaces, array, symmetric=True):
    assert array.ndim == 2
    assert array.shape[0] == array.shape[1]
    sym = pyadcman.Symmetry(mospaces, "bb", {"b": (array.shape[0], 0)})
    if symmetric:
        sym.permutations = ["ij", "ji"]
    tensor = pyadcman.Tensor(sym)
    tensor.set_from_ndarray(array)
    return tensor


def check_ppadc(refstate, n_states=None, n_singlets=None,
                n_triplets=None, n_spin_flip=None, **kwargs):
    if not refstate.restricted or refstate.spin_multiplicity != 1:
        if n_singlets is not None:
            raise ValueError(
                'The key "n_singlets" may only be used in '
                "combination with an restricted ground state "
                "reference of singlet spin to provide the number "
                'of excited states to compute. Use "n_states" '
                "for an UHF reference."
            )
        if n_triplets is not None:
            raise ValueError(
                'The key "n_triplets" may only be used in '
                "combination with an restricted ground state "
                "reference of singlet spin to provide the number "
                'of excited states to compute. Use "n_states" '
                "for an UHF reference."
            )

        n_singlets = 0
        n_triplets = 0
        if (
            n_states is not None
            and n_states > 0
            and n_spin_flip is not None
            and n_spin_flip > 0
        ):
            raise ValueError(
                "Can only use one of n_states or n_spin_flip simultaneously."
            )

        if n_spin_flip is not None:
            n_states = n_spin_flip
        else:
            n_spin_flip = 0
    else:
        if n_states is not None:
            raise ValueError(
                'The key "n_states" may only be used in '
                "combination with an unrestricted ground state "
                "or a non-singlet ground state to provide the "
                "number of excited states to compute. Use "
                '"n_singlets" and "n_triplets".'
            )
        if n_spin_flip is not None:
            raise ValueError(
                'The key "n_spin_flip" may only be used in '
                "combination with an unrestricted ground state."
            )

        n_spin_flip = 0
        n_states = 0
        if n_triplets is None:
            n_triplets = 0
        if n_singlets is None:
            n_singlets = 0

    if n_singlets + n_states + n_triplets == 0:
        raise ValueError("No excited states to compute.")

    for (arg, value) in kwargs.items():
        if value is None:
            continue
        if value > 0:
            raise ValueError(f"For PP-ADC calculations, {arg} should not be set.")
    return n_states, n_singlets, n_triplets, n_spin_flip


def check_ipadc(refstate, n_ipalpha=None, n_ipbeta=None, **kwargs):
    if not refstate.restricted or refstate.spin_multiplicity != 1:
        if n_ipalpha is None:
            n_ipalpha = 0
    else:
        if n_ipalpha is not None:
            raise ValueError(
                'The key "n_ipalpha" may only be used in '
                "combination with an unrestricted ground state "
                'reference. Use "n_ipbeta" for an RHF reference.'
            )
        n_ipalpha = 0

    if n_ipbeta is None:
        n_ipbeta = 0
    if n_ipalpha + n_ipbeta == 0:
        raise ValueError("No ionisation states to compute.")

    for (arg, value) in kwargs.items():
        if value is None:
            continue
        if value > 0:
            raise ValueError(f"For IP-ADC calculations, {arg} should not be set.")
    return n_ipalpha, n_ipbeta


def run_adcman(
    data,
    method,
    core_orbitals=[],
    frozen_core=[],
    frozen_virtual=[],
    n_singlets=None,
    n_triplets=None,
    n_states=None,
    n_spin_flip=None,
    max_subspace=0,
    conv_tol=1e-6,
    max_iter=60,
    print_level=1,
    residual_min_norm=1e-12,
    n_guess_singles=0,
    n_guess_doubles=0,
    n_guess_h=0,
    n_guess_p2h=0,
    n_ipalpha=None,
    n_ipbeta=None,
    ground_state_density=None,
):
    """
    Run adcman to solve an ADC problem.

    Parameters
    ----------
    data : adcc.HdfProvider or h5py.File or str
        SCF data to run ADC upon

    method : str
        ADC method to execute

    core_orbitals : list
        The orbitals to be put into the core-occupied space.

    frozen_core : list
        The orbitals to select as frozen core orbitals (i.e. inactive occupied
        orbitals for both the MP and ADC methods performed).

    frozen_virtual : list
        The orbitals to select as frozen virtual orbitals (i.e. inactive
        virtuals for both the MP and ADC methods performed).

    n_singlets : int or NoneType
        Number of singlets to solve for (has to be None for UHF reference)

    n_triplets : int or NoneType
        Number of triplets to solve for (has to be None for UHF reference)

    n_states : int or NoneType
        Number of states to solve for (has to be None for RHF reference)

    n_spin_flip : int or NoneType
        Number of spin-flip states to be computed (has to be None for
        RHF reference)

    max_subspace : int
        Maximal subspace size (0 means choose automatically depending
        on the number of states to compute)

    conv_tol : float
        Convergence tolerance on the l2 norm of residuals to consider
        them converged

    max_iter : int
        Maximal numer of iterations

    print_level : int
        ADCman print level

    residual_min_norm : float
        Minimal norm a residual needs to have in order to be accepted as a new
        subspace vector (defaults to 1e-12)

    n_guess_singles : int
        Number of singles block guesses. If this plus n_guess_doubles is less
        than then the number of states to be computed, then n_guess_singles =
        number of excited states to compute

    n_guess doubles : int
        Number of doubles block guesses. If this plus n_guess_singles is less
        than then the number of states to be computed, then n_guess_singles =
        number of excited states to compute

    n_guess_h : int
        Number of hole block guesses for IP-ADC. If this plus n_guess_p2h
        is less than the number of states to be computed than n_guess_h =
        number of ipstates to compute

    n_guess_p2h : int
        Number of particle-two-hole block guesses for IP-ADC. If this
        plus n_guess_p2h is less than the number of states to be computed
        than n_guess_h = number of ipstates to compute

    n_ipalpha : int or NoneType
        Number of alpha-ionized states to solve for
        (i.e. one beta electron is removed; has to be None
        for RHF reference)

    n_ipbeta : int or NoneType
        Number of beta-ionized states to solve for
        (i.e. one alpha electron is removed)

    ground_state_density : str or NoneType
        Ground state density to use for 3rd order ADC methods. Can be "mp2"
        (the default), "mp3" or "dyson", which implies iterating the MP3 density
        using the dyson expansion method until convergence.
    """
    if isinstance(data, str) and data.endswith(".hdf5"):
        data = HdfProvider(h5py.File(data, "r"))
    if isinstance(data, h5py.File):
        data = HdfProvider(data)
    if not isinstance(data, HdfProvider):
        raise TypeError("data needs to be an HdfProvider instance")
    refstate = pyadcman.ReferenceState(data, core_orbitals, frozen_core,
                                       frozen_virtual)

    # Parse ADC method into base method and variants
    if method not in get_valid_methods():
        raise ValueError("Invalid ADC method: " + method)

    adc_variant = []
    split = method.split("-")
    base_method = split[-1]
    split = split[:-1]
    if "cvs" in split:
        adc_variant.append("cvs")  # core-valence-separation
    # Also supported by adcman, but not adcc:
    #   adc_variant.append("sos")  # spin-opposite-scaled
    #   adc_variant.append("ri")   # resolution-of-identity

    # Check consistency of requested states
    checkargs = dict(n_states=n_states, n_singlets=n_singlets,
                     n_triplets=n_triplets, n_spin_flip=n_spin_flip,
                     n_ipalpha=n_ipalpha, n_ipbeta=n_ipbeta)
    if base_method.startswith("ip"):
        ret = check_ipadc(refstate, **checkargs)
        n_ipalpha, n_ipbeta = ret
    else:
        ret = check_ppadc(refstate, **checkargs)
        n_states, n_singlets, n_triplets, n_spin_flip = ret
        if n_spin_flip > 0:
            adc_variant.append("sf")  # spin-flip

    if "cvs" in adc_variant and not refstate.has_core_occupied_space:
        raise ValueError("Cannot request CVS variant if no core "
                         "orbitals selected.")
    if refstate.has_core_occupied_space and "cvs" not in adc_variant:
        raise ValueError("Cannot request core orbitals without CVS variant.")

    # Build adcman parameter tree
    params = tasks.parameters(
        # General
        base_method,
        adc_variant,
        print_level=print_level,
        restricted=refstate.restricted,
        solver="davidson",
        conv_tol=conv_tol,
        residual_min_norm=residual_min_norm,
        max_iter=max_iter,
        max_subspace=max_subspace,
        ground_state_density=ground_state_density,
        # PP-ADC
        n_states=n_states,
        n_singlets=n_singlets,
        n_triplets=n_triplets,
        n_guess_singles=n_guess_singles,
        n_guess_doubles=n_guess_doubles,
        # IP-ADC
        n_ipalpha=n_ipalpha,
        n_ipbeta=n_ipbeta,
        n_guess_h=n_guess_h,
        n_guess_p2h=n_guess_p2h,
    )

    # Build adcman context tree
    incontext = refstate.to_ctx()

    # Nuclear dipole moment
    nucmm = [refstate.nuclear_total_charge] + refstate.nuclear_dipole
    incontext["ao/nucmm"] = nucmm + 6 * [0.0]

    # Electric dipole integrals
    integrals_ao = data.operator_integral_provider
    for i, comp in enumerate(["x", "y", "z"]):
        dip_bb = as_tensor_bb(
            refstate.mospaces, integrals_ao.electric_dipole[i], symmetric=True
        )
        incontext["ao/d{}_bb".format(comp)] = dip_bb

    return pyadcman.run(incontext, params)
