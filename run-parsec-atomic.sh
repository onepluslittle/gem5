./build/X86/gem5.opt \
--outdir=$2/atomic_$1t \
./configs/example/fs.py -n 8 \
--script=benchmarks/$2_$1c_simsmall.rcS \
--kernel=parsec_images/system/binaries/x86_64-vmlinux-2.6.28.4-smp
# -s 1 \
# -r 1 \