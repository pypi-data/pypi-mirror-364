#!/usr/bin/env python3
"""
InfraDSL VM Examples

This file demonstrates different VM creation patterns using the InfraDSL syntax.
"""

from infradsl import GoogleCloud, InstanceSize, Region

# Simple VM Example for Google Cloud
vm = (
    GoogleCloud.VM("simple-notif-vm")
    .ubuntu(22_04)
    .size(InstanceSize.SMALL)
    .zone(Region.EUROPE_WEST1_B)
    .disk(20)
    .public_ip(True)
    .environment("development")
    .labels(project="demo", notifications="auto")
)

# AWS Example with monitoring and automatic remediation
from infradsl import AWS

aws_vm = (
    AWS.EC2("ix-sto1-aws-whatever01")
    .ubuntu(22_04)
    .size(InstanceSize.SMALL)
    .zone(Region.US_EAST1)
    .disk(20)
    .public_ip(False)
    .environment("ureg")
    .labels(project="game-server", drift_detection="enabled")
    .auto_scale(min_size=2, max_size=4)
    .check_state(
        check_interval=DriftCheckInterval.ONE_HOUR,
        auto_remediate="NOTIFY",
    )
)
