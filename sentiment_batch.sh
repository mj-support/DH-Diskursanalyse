#!/bin/bash
#SBATCH --job-name=mistall
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --time=20:00:00
#SBATCH --partition=clara
#SBATCH --gpus=v100
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --nodes=1
#SBATCH --ntasks=1

# Start des Trainings
python3 sentiment_analysis.py
