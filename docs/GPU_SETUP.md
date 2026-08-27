# GPU setup notes

This guide explains how to prepare an NVIDIA GPU machine for running the full Cinono AI pipeline locally.

1) Install NVIDIA driver and CUDA toolkit compatible with your GPU.
2) Create a Python virtual environment (recommended Python 3.10+).
3) Install PyTorch with CUDA following https://pytorch.org (choose the correct CUDA version).
4) Install diffusers and related packages:
   pip install diffusers transformers accelerate safetensors
5) Install RQ and Redis (the worker uses Redis):
   sudo apt-get install redis-server
   pip install rq redis
6) Install other ML/audio dependencies:
   pip install audiocraft TTS whisperx soundfile ffmpeg-python

Troubleshooting:
- If torch.cuda.is_available() returns False, ensure NVIDIA driver and CUDA are correctly installed and that the CUDA toolkit version matches the installed torch build.

Recommended machine: any modern NVIDIA GPU with >= 8 GB VRAM (RTX 2070 / 3060 / A10 / A100).
