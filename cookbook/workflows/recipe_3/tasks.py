from __future__ import absolute_import
from __future__ import print_function
import random

from flytekit.sdk.tasks import inputs, outputs, python_task
from flytekit.sdk.types import Types
from flytekit.sdk.tasks import inputs, outputs, dynamic_task

from flytekit.sdk.tasks import inputs, outputs, python_task
from flytekit.sdk.types import Types
from flytekit.sdk.workflow import workflow_class, Input, Output


@inputs(custom=Types.Generic)
@outputs(counts=Types.Generic)
@python_task
def generic_type_task(wf_params, custom, counts):
    # Go through each of the values of the input and if it's a str, count the length
    wf_params.logging.info("Running custom object task")
    results = {}
    for k, v in custom:
        if type(v) == str:
            results[k] = len(v)
        else:
            results[k] = v

    counts.set(results)


@workflow_class
class GenericDemoWorkflow(object):
    a = Input(Types.Generic, default=5, help="Input for inner workflow")
    odd_nums_task = generic_type_task(custom=a)
    task_output = Output(odd_nums_task.outputs.out, sdk_type=Types.Integer)

