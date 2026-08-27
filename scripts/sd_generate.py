"""Stable Diffusion image generation script using diffusers.

Requires: torch, diffusers, accelerate. Run on a GPU machine (CUDA).

Usage:
  python scripts/sd_generate.py --prompt "A cinematic portrait" --out outputs/img.png

If diffusers or torch are not available, the script will exit with a helpful message.
"""
import argparse
import sys
import os


def main():
    parser = argparse.ArgumentParser("sd_generate")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=20)
    args = parser.parse_args()

    try:
        import torch
        from diffusers import StableDiffusionPipeline
    except Exception as e:
        print("Missing diffusers/torch. Install per docs/GPU_SETUP.md. Error:", e)
        sys.exit(2)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Using device:", device)

    model_id = os.getenv("SD_MODEL_ID", "runwayml/stable-diffusion-v1-5")
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16 if device=="cuda" else torch.float32)
    pipe = pipe.to(device)

    image = pipe(args.prompt, height=args.height, width=args.width, num_inference_steps=args.steps).images[0]
    out_path = args.out
    image.save(out_path)
    print("Wrote image to", out_path)

if __name__ == "__main__":
    main()
