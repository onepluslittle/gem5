#!/usr/bin/env python2.7

import os
import re
import sys
import random
import sh
import time
from os.path import join as pjoin
from os.path import expanduser as uexp
from multiprocessing import Pool

cmd_timestamp = None


def run(benchmark):
    global cmd_timestamp

    gem5_dir = os.environ['gem5_root']
    outdir = pjoin(uexp('~/gem5-results/simpoint-profile'), benchmark)

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    if cmd_timestamp:
        output_timestamp_file = pjoin(outdir, 'done')
        if os.path.isfile(output_timestamp_file):
            file_m_time = os.path.getmtime(output_timestamp_file)
            if file_m_time > cmd_timestamp:
                print('Command is older than output of {}, skip!'.format(
                    benchmark))
                return

    exec_dir = os.environ['gem5_run_dir']
    os.chdir(exec_dir)

    options = [
            '--outdir=' + outdir,
            pjoin(gem5_dir, 'configs/spec2006/se_spec06.py'),
            '--spec-2006-bench',
            '-b',
            '{}'.format(benchmark),
            '--benchmark-stdout={}/out'.format(outdir),
            '--benchmark-stderr={}/err'.format(outdir),
            '--cpu-type=AtomicSimpleCPU',
            '--fastmem',
            '--simpoint-profile',
            '--simpoint-interval={}'.format(200*10**6),
            '-I {}'.format(1000*10**9),
            '--mem-size=4GB',
            ]
    print(options)
    gem5 = sh.Command(pjoin(os.environ['gem5_build'], 'gem5.opt'))
    # sys.exit(0)
    gem5(
            _out=pjoin(outdir, 'gem5_out.txt'),
            _err=pjoin(outdir, 'gem5_err.txt'),
            *options
            )

    sh.touch(pjoin(outdir, 'done'))

def main():
    num_thread = 27

    benchmarks = []

    cmd_timestamp_file = './ts-simprofile'
    global cmd_timestamp
    if os.path.isfile(cmd_timestamp_file):
        cmd_timestamp = os.path.getmtime(cmd_timestamp_file)
        print(cmd_timestamp)


    with open('./all_compiled_spec.txt') as f:
        for line in f:
            benchmarks.append(line.strip())
    # print benchmarks

    if num_thread > 1:
        p = Pool(num_thread)
        p.map(run, benchmarks)
    else:
        run(benchmarks[0])


if __name__ == '__main__':
    main()
