# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from inspect import signature
from typing import Callable

from digitalhub.utils.generic_utils import encode_string
from hera.workflows import Workflow


def run_hera_build(pipeline: Callable, *args, **kwargs) -> dict:
    """
    Build Hera pipeline as YAML.

    Parameters
    ----------
    pipeline : Callable
        Hera pipeline function.

    Returns
    -------
    dict
        Pipeline spec.
    """
    workflow_parameters = {}
    for param in signature(pipeline).parameters.values():
        workflow_parameters[param.name] = r"{{inputs.parameters." + param.name + r"}}"
    workflow = pipeline(**workflow_parameters)
    if not isinstance(workflow, Workflow):
        raise TypeError(f"Expected Hera Workflow, got {type(workflow)}. Your function must return a Hera Workflow.")
    return {"workflow": encode_string(workflow.to_yaml())}
