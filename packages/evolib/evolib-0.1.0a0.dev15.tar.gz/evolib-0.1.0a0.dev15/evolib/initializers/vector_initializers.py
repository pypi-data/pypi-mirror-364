# SPDX-License-Identifier: MIT
"""Initializers for ParaVector representations."""

from typing import TYPE_CHECKING, Callable

import numpy as np

from evolib.config.schema import ComponentConfig

if TYPE_CHECKING:
    from evolib.core.population import Pop

from evolib.representation.vector import ParaVector


def random_initializer(cfg: ComponentConfig) -> Callable[["Pop"], ParaVector]:

    def init_fn(_: "Pop") -> ParaVector:
        pv = ParaVector()
        pv.apply_config(cfg)

        if pv.init_bounds is None:
            raise ValueError("init_bounds must be defined")
        if pv.dim is None:
            raise ValueError("dim must be defined")

        pv.vector = np.random.uniform(pv.init_bounds[0], pv.init_bounds[1], size=pv.dim)
        return pv

    return init_fn


def zero_initializer(cfg: ComponentConfig) -> Callable[["Pop"], ParaVector]:

    def init_fn(_: "Pop") -> ParaVector:
        pv = ParaVector()
        pv.apply_config(cfg)
        pv.vector = np.zeros(pv.dim)
        return pv

    return init_fn


def fixed_initializer(cfg: ComponentConfig) -> Callable[["Pop"], ParaVector]:
    values = np.array(cfg.values)

    def init_fn(_: "Pop") -> ParaVector:
        pv = ParaVector()
        pv.apply_config(cfg)
        pv.vector = values.copy()
        return pv

    return init_fn


def normal_initializer(cfg: ComponentConfig) -> Callable[["Pop"], ParaVector]:
    mean = float(cfg.mean or 0.0)
    std = float(cfg.std or 1.0)

    def init_fn(_: "Pop") -> ParaVector:
        pv = ParaVector()
        pv.apply_config(cfg)
        pv.vector = np.random.normal(loc=mean, scale=std, size=pv.dim)
        return pv

    return init_fn


def vector_adaptive_initializer(cfg: ComponentConfig) -> Callable[["Pop"], ParaVector]:

    def init_fn(_: "Pop") -> ParaVector:
        pv = ParaVector()
        pv.apply_config(cfg)

        if pv.init_bounds is None:
            raise ValueError("init_bounds must be defined")
        if pv.dim is None:
            raise ValueError("dim must be defined")
        if pv.min_mutation_strength is None or pv.max_mutation_strength is None:
            raise ValueError(
                "min_mutation_strength and max_mutation_strength" "must be defined."
            )

        pv.vector = np.random.uniform(pv.init_bounds[0], pv.init_bounds[1], size=pv.dim)
        if pv.randomize_mutation_strengths:
            pv.para_mutation_strengths = np.random.uniform(
                pv.min_mutation_strength, pv.max_mutation_strength, size=pv.dim
            )
        else:
            if pv.mutation_strength is None:
                raise ValueError(
                    "mutation_strength must be defined for non-random"
                    "initialization of para_mutation_strengths."
                )
            pv.para_mutation_strengths = np.full(pv.dim, pv.mutation_strength)
        return pv

    return init_fn
