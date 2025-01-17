Executing Distributed Pytorch training jobs on K8s
==========================================================
This plugin uses the Kubeflow Pytorch Operator and provides an extremely simplified interface for executing distributed training using various pytorch backends.

Installation
------------

To use the flytekit distributed pytorch plugin simply run the following:

.. prompt:: bash

   pip install flytekitplugins-kfpytorch


How to build your Dockerfile for Pytorch on K8s
-----------------------------------------------

.. note::

    If using CPU for training then special dockerfile is NOT REQUIRED. If GPU or TPUs are required then, the dockerfile differs only in the driver setup. The following dockerfile is enabled for GPU accelerated training using CUDA

.. code-block:: docker
    :emphasize-lines: 1
    :linenos:

    FROM pytorch/pytorch:1.7.0-cuda11.0-cudnn8-runtime
    LABEL org.opencontainers.image.source https://github.com/flyteorg/flytesnacks
    
    WORKDIR /root
    ENV LANG C.UTF-8
    ENV LC_ALL C.UTF-8
    ENV PYTHONPATH /root
    
    # Install basics
    RUN apt-get update && apt-get install -y make build-essential libssl-dev curl
    
    # Install the AWS cli separately to prevent issues with boto being written over
    RUN pip install awscli
    
    ENV VENV /opt/venv
    # Virtual environment
    RUN python3 -m venv ${VENV}
    ENV PATH="${VENV}/bin:$PATH"
    
    # Install Python dependencies
    COPY kubernetes/kfpytorch/requirements.txt /root
    RUN pip install -r /root/requirements.txt
    
    # Copy the makefile targets to expose on the container. This makes it easier to register.
    COPY in_container.mk /root/Makefile
    COPY kubernetes/kfpytorch/sandbox.config /root
    
    # Copy the actual code
    COPY kubernetes/kfpytorch/ /root/kfpytorch/
    
    # This tag is supplied by the build script and will be used to determine the version
    # when registering tasks, workflows, and launch plans
    ARG tag
    ENV FLYTE_INTERNAL_IMAGE $tag
    