# Copyright (c) 2017 ARM Limited
# All rights reserved.
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Andreas Sandberg
#          Stephan Diestelhorst

# This configuration file extends the example ARM big.LITTLE(tm)
# with example power models.

from __future__ import print_function

import argparse
import os

import m5
from m5.objects import MathExprPowerModel, PowerModel

import fs_bigLITTLE as bL


class CpuPowerOn(MathExprPowerModel):
    # 2A per IPC, 3pA per cache miss
    # and then convert to Watt
    dyn = "voltage * (2 * ipc + " \
            "3 * 0.000000001 * dcache.overall_misses / sim_seconds)"
    st = "4 * temp"

class CpuPowerOff(MathExprPowerModel):
    dyn = "0"
    st = "0"

class CpuPowerModel(PowerModel):
    pm = [
        CpuPowerOn(), # ON
        CpuPowerOff(), # CLK_GATED
        CpuPowerOff(), # SRAM_RETENTION
        CpuPowerOff(), # OFF
    ]


def main():
    parser = argparse.ArgumentParser(
        description="Generic ARM big.LITTLE configuration with "\
        "example power models")
    bL.addOptions(parser)
    options = parser.parse_args()

    if options.cpu_type != "timing":
        m5.fatal("The power example script requires 'timing' CPUs.")

    root = bL.build(options)

    # Wire up some example power models to the CPUs
    for cpu in root.system.descendants():
        if not isinstance(cpu, m5.objects.BaseCPU):
            continue

        cpu.default_p_state = "ON"
        cpu.power_model = CpuPowerModel()

    bL.instantiate(options)

    print("*" * 70)
    print("WARNING: The power numbers generated by this script are "
        "examples. They are not representative of any particular "
        "implementation or process.")
    print("*" * 70)

    # Dumping stats periodically
    m5.stats.periodicStatDump(m5.ticks.fromSeconds(0.1E-3))
    bL.run()


if __name__ == "__m5_main__":
    main()
