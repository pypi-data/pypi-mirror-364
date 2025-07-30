#!/usr/bin/env python3
"""
Test script to verify VirtualMachine methods directly
"""
from infradsl import InstanceSize, DigitalOcean, DriftAction

# Create a VirtualMachine instance with metadata and spec using the proper factory
vm = (
    DigitalOcean.VM("DigitalOceanVM")
    .ubuntu()
    .size(InstanceSize.SMALL)
    .ssh_key("~/.ssh/id_rsa.pub")
    .disk(20)
    .public_ip()
    .environment("development")
    .drift_policy(DriftAction.IGNORE)
)
