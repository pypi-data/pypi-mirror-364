#!/usr/bin/env python3
"""
Test script to verify VirtualMachine methods directly
"""
from infradsl import InstanceSize, GoogleCloud, DriftAction
from infradsl.resources.compute.virtual_machine import VirtualMachine

vm2 = (
    VirtualMachine("whatever01")
    .ubuntu()
    .with_provider(GoogleCloud)
    .size(InstanceSize.SMALL)
    .ssh_key("~/.ssh/id_ed25519.pub")
    .disk(20)
    .public_ip()
    .drift_policy(DriftAction.REVERT)
)
