# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import os
from uuid import uuid4

from digitalhub.entities.function.crud import get_function
from digitalhub.entities.workflow.crud import get_workflow
from digitalhub.runtimes.enums import RuntimeEnvVar
from digitalhub.stores.credentials.enums import CredsEnvVar
from hera.workflows import DAG, Artifact, Container, Parameter, Steps, Task
from hera.workflows import models as m
from hera.workflows._context import _context



def step(**step_kwargs):
    arguments = step_kwargs.pop("parameters", None)
    inner_ctx = _context.pieces[-1]
    if isinstance(inner_ctx, DAG):
        op_type = "dag-op-"
    elif isinstance(inner_ctx, Steps):
        op_type = "step-op-"
    else:
        raise ValueError("step() can only be called inside a DAG or Steps")
    _context.pieces = _context.pieces[:-1]
    container = container_op(**step_kwargs)
    _context.pieces.append(inner_ctx)
    name = op_type + step_kwargs.get("name", "") + "-" + uuid4().hex
    return Task(name=name, template=container, arguments=arguments)


def container_op(
    template: dict,
    function: str | None = None,
    function_id: str | None = None,
    workflow: str | None = None,
    workflow_id: str | None = None,
    name: str | None = None,
    inputs: list | None = None,
    outputs: list | None = None,
    **kwargs,
) -> None:
    """
    Create a Hera container template.

    Parameters
    ----------
    template : dict
        Parameters template to pass to function.run() or workflow.run().
    function : str
        Function name.
    function_id : str
        Function ID.
    workflow : str
        Workflow name.
    workflow_id : str
        Workflow ID.
    name : str
        Step name.
    inputs : list
        Step inputs.
    outputs : list
        Step outputs.

    Returns
    -------
    Container
        Hera container template.
    """

    cmd = ["python"]
    args = ["step.py"]

    # Add entity
    try:
        project = os.environ.get(RuntimeEnvVar.PROJECT.value)
        if function is not None:
            exec_entity = get_function(function, project=project, entity_id=function_id)
        elif workflow is not None:
            exec_entity = get_workflow(workflow, project=project, entity_id=workflow_id)
        else:
            raise RuntimeError("Either function or workflow must be provided.")
    except Exception as e:
        raise RuntimeError("Function or workflow not found.") from e
    args.extend(["--entity", str(exec_entity.key)])

    # Add kwargs
    template["wait"] = True
    args.extend(["--kwargs", json.dumps(template, cls=PipelineParamEncoder)])

    # Get image stepper
    image = os.environ.get(CredsEnvVar.DHCORE_WORKFLOW_IMAGE.value)
    if image is None:
        raise RuntimeError(f"Env var '{CredsEnvVar.DHCORE_WORKFLOW_IMAGE.value}' is not set")

    # Get step outputs
    outputs = outputs if outputs is not None else []
    step_outputs = []
    for o in outputs:
        path = "/tmp/entity_" + str(o).replace(".", "_").replace("/", "_")
        step_outputs.append(Artifact(name=o, path=path))
        step_outputs.append(Parameter(name=o, value_from=m.ValueFrom(path=path), output=True))

    # Get step inputs
    inputs = inputs if inputs is not None else []
    step_inputs = [Parameter(name=i) for i in inputs]

    # Get step name
    name = name if name is not None else uuid4().hex

    return Container(
        name=name,
        image=image,
        command=cmd,
        args=args,
        outputs=step_outputs,
        inputs=step_inputs,
    )


class PipelineParamEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Parameter):
            return obj.value
        return super().default(obj)
