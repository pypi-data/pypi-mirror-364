#!/bin/bash
#SBATCH --out=logs/debug.out
#SBATCH --err=logs/debug.err
#SBATCH -A cin_staff
#SBATCH -p boost_usr_prod
#SBATCH -N 1                # 1 node
##SBATCH --ntasks-per-node=4 # 1 task
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:4     # 1 gpus per node out of 4
##########SBATCH --exclusive
#SBATCH --qos=boost_qos_dbg
  



export GPUS_PER_NODE=4
export HOSTNAMES=`scontrol show hostnames "$SLURM_JOB_NODELIST"`
export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export COUNT_NODE=`scontrol show hostnames "$SLURM_JOB_NODELIST" | wc -l`
export MASTER_PORT=6000
export NNODES=$SLURM_NNODES
export NODE_RANK=$SLURM_PROCID
export WORLD_SIZE=$(($GPUS_PER_NODE*$NNODES))
export MASTER_ADDR_IP=$(srun --nodes=1 --ntasks=1 -w "$MASTER_ADDR" hostname --ip-address)
export BNB_CUDA_VERSION=121

echo myuser=`whoami`
echo COUNT_NODE=$COUNT_NODE
echo hostname = `hostname`
echo HOSTNAMES = $HOSTNAMES
echo MASTER_ADDR= $MASTER_ADDR
echo MASTER_PORT= $MASTER_PORT
echo SLURM_PROCID= $SLURM_PROCID
echo NNODES= $NNODES    
echo WORLD_SIZE= $WORLD_SIZE    
echo NODE_RANK= $NODE_RANK      
echo NODE_NAME = $SLURMD_NODENAME
echo MASTER_ADDR_IP = $MASTER_ADDR_iP



nodes=( $( scontrol show hostnames $SLURM_JOB_NODELIST ) )
nodes_array=($nodes)
head_node=${nodes_array[0]}
head_node_ip=$(srun --nodes=1 --ntasks=1 -w "$head_node" hostname --ip-address)

export NCCL_DEBUG_SUBSYS=ALL
export NCCL_SOCKET_IFNAME=ib0
export NCCL_IB_SL=1
export UCX_IB_SL=1
export NVSHMEM_IB_SL=1
export NVSHMEM_DISABLE_NCCL=1
export TORCH_NCCL_BLOCKING_WAIT=1
export NCCL_NET=Socket

# export LD_LIBRARY_PATH=/leonardo_scratch/large/userinternal/rscheda0/distributed-asynchronous-checkpointing/dac2/lib/python3.11/site-packages/nvidia/nvjitlink/lib:$LD_LIBRARY_PATH
# export HF_HOME="/leonardo_scratch/large/userinternal/rscheda0"
# export HF_DATASETS_CACHE="/leonardo_scratch/large/userinternal/rscheda0/hf_cache"

module load cuda/12.1
#source /leonardo_scratch/large/userinternal/rscheda0/turtles/.venv/bin/activate

srun uv run /leonardo_scratch/large/userinternal/rscheda0/turtles/gpus.py
