#!/bin/bash -l
#SBATCH --job-name=synverse_a100_2
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err
#SBATCH --time=24:00:00
#SBATCH --partition=a100
#SBATCH --gres=gpu:a100:1
# SBATCH --partition=v100
# SBATCH --gres=gpu:v100:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --export=NONE

unset SLURM_EXPORT_ENV

echo "Job ID     : $SLURM_JOB_ID"
echo "Node       : $SLURMD_NODENAME"
echo "GPU        : $CUDA_VISIBLE_DEVICES"
echo "Start time : $(date)"
echo "TMPDIR     : $TMPDIR"

export http_proxy=http://proxy.nhr.fau.de:80
export https_proxy=http://proxy.nhr.fau.de:80

module load python/3.12-conda
conda activate nextflow25

echo "[$(date +%H:%M:%S)] Extracting dataset..."
unzip $WORK/nf_core_synverse/dataset/inputs.zip -d $TMPDIR
echo "[$(date +%H:%M:%S)] Dataset ready."
ls $TMPDIR/inputs

cd $HOME/synverse

RESOLVED_CFG=/tmp/resolved_config_${SLURM_JOB_ID}.yaml
envsubst < assets/testdata/Cluster_Config.yaml > $RESOLVED_CFG

echo "[$(date +%H:%M:%S)] Resolved config input_dir line:"
grep input_dir $RESOLVED_CFG

echo "[$(date +%H:%M:%S)] Starting Nextflow..."
nextflow run . \
  -profile conda,gpu \
  --input $RESOLVED_CFG \
  -work-dir $WORK/synverse/regular_work_a100 \
  --outdir $WORK/synverse/regular_results_a100

EXIT_CODE=$?
echo "Pipeline finished at $(date)"
echo "Exit code: $EXIT_CODE"
exit $EXIT_CODE