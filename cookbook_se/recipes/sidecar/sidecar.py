import time
import os

from flytekit import task, workflow
from flytekit.taskplugins.sidecar import Sidecar

from k8s.io.api.core.v1 import generated_pb2
from k8s.io.apimachinery.pkg.api.resource.generated_pb2 import Quantity

_SHARED_DATA_PATH = '/data/message.txt'


# A simple pod spec in which a shared volume is mounted in both the primary and secondary containers. The secondary
# writes a file that the primary waits on before completing.
def generate_pod_spec_for_task():
    pod_spec = generated_pb2.PodSpec()

    primary_container = generated_pb2.Container(name="primary")

    secondary_container = generated_pb2.Container(
              name="secondary",
              image="alpine",
    )
    secondary_container.command.extend(["/bin/sh"])
    secondary_container.args.extend(["-c", "echo hi sidecar world > {}".format(_SHARED_DATA_PATH)])

    resources = generated_pb2.ResourceRequirements()
    resources.limits["cpu"].CopyFrom(Quantity(string="1"))
    resources.requests["cpu"].CopyFrom(Quantity(string="1"))
    resources.limits["memory"].CopyFrom(Quantity(string="100Mi"))
    resources.requests["memory"].CopyFrom(Quantity(string="100Mi"))
    primary_container.resources.CopyFrom(resources)
    secondary_container.resources.CopyFrom(resources)

    shared_volume_mount = generated_pb2.VolumeMount(
              name="shared-data",
              mountPath="/data",
    )
    secondary_container.volumeMounts.extend([shared_volume_mount])
    primary_container.volumeMounts.extend([shared_volume_mount])

    pod_spec.volumes.extend([generated_pb2.Volume(
               name="shared-data",
               volumeSource=generated_pb2.VolumeSource(
                   emptyDir=generated_pb2.EmptyDirVolumeSource(
                              medium="Memory",
                   )
               )
    )])
    pod_spec.containers.extend([primary_container, secondary_container])
    return pod_spec


@task(task_config=Sidecar(
    pod_spec=generate_pod_spec_for_task(),
    primary_container_name="primary",
)
def my_sidecar_task(shared_message: str) -> str:
    # The code defined in this task will get injected into the primary container.
    while not os.path.isfile(_SHARED_DATA_PATH):
        time.sleep(5)

    with open(_SHARED_DATA_PATH, 'r') as shared_message_file:
        shared_message.set(shared_message_file.read())


@workflow
class SidecarWorkflow(shared_message: str):
    s = my_sidecar_task(shared_message)