#!/bin/bash
# The interpreter used to execute the script

#“#SBATCH” directives that convey submission options:

#SBATCH --job-name=get_counts_binary
#SBATCH --mail-type=BEGIN,END
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --mem-per-cpu=5000m 
#SBATCH --time=5:00:00
#SBATCH --account=ebruch0
#SBATCH --partition=standard

/bin/hostname
python get_counts_binary.py