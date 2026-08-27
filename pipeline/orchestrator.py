"""Orchestrator: runs the entire pipeline for a single prompt.
This module is called by the worker via RQ.

Behavior:
- Rewrites prompt to a timed script (scripts/rewriter.py)
- Plans scenes (scripts/planner.py)
- Generates images per scene (scripts/sd_generate.py)
- Animates images into frames (scripts/gen_frames.py or scripts/animate.py)
- Optionally runs RIFE interpolation (user-installed)
- Generates TTS (scripts/tts.py)
- Generates music (scripts/musicgen.py)
- Generates captions (scripts/captions.py)
- Composes final video (scripts/compose.py)
- Detects hooks and exports (scripts/detect_hooks.py, scripts/make_hooks.py)
- Uploads using uploader stubs (uploader/*)

Note: most heavy model steps require a GPU and the appropriate Python packages (torch, diffusers, accelerate, etc.). See docs/GPU_SETUP.md for instructions.
"""
import os
import subprocess
import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / "runs"
WORK_DIR.mkdir(exist_ok=True)


def _run(cmd, cwd=None, env=None):
    print("RUN:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd or ROOT, env=env or os.environ)


def process_job(prompt: str, platforms: list[str], aspect: str = "9:16"):
    """Main entry point for processing a single prompt end-to-end.
    Returns a JSON file with outputs and uploads (if uploader credentials are provided).
    """
    run_id = uuid.uuid4().hex[:8]
    out_dir = WORK_DIR / f"run_{run_id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "run_id": run_id,
        "prompt": prompt,
        "platforms": platforms,
        "aspect": aspect,
        "out_dir": str(out_dir)
    }

    # 1) Rewriter: produce an expanded timed script
    rew_path = out_dir / "script.json"
    _run(["python", "scripts/rewriter.py", "--prompt", prompt, "--out", str(rew_path)])

    # 2) Planner: scene list with prompts and durations
    scenes_path = out_dir / "scenes.json"
    _run(["python", "scripts/planner.py", "--script", str(rew_path), "--out", str(scenes_path)])

    # 3) Image generation per scene
    images_dir = out_dir / "images"
    images_dir.mkdir(exist_ok=True)
    with open(scenes_path) as f:
        scenes = json.load(f)
    for i, s in enumerate(scenes):
        prompt_text = s.get("prompt")
        img_out = images_dir / f"scene_{i:02d}.png"
        _run(["python", "scripts/sd_generate.py", "--prompt", prompt_text, "--out", str(img_out)])

    # 4) Animate images into frames (uses Ken Burns fallback if heavy libs not installed)
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(exist_ok=True)
    # If an animate script exists, use it; otherwise gen_frames.py can pan/zoom a single image per scene
    for i, s in enumerate(scenes):
        img_in = images_dir / f"scene_{i:02d}.png"
        scene_frames = frames_dir / f"scene_{i:02d}"
        _run(["python", "scripts/gen_frames.py", "--image", str(img_in), "--out", str(scene_frames), "--frames", str(int(s.get("duration", 3) * 30))])

    # 5) Stitch scene frames into a single video
    stitched_video = out_dir / "raw_video.mp4"
    # Create a concat list
    concat_txt = out_dir / "concat.txt"
    with open(concat_txt, "w") as f:
        for i, s in enumerate(scenes):
            scene_frames = frames_dir / f"scene_{i:02d}"
            # produce a temporary mp4 for this scene
            tmp_scene = out_dir / f"scene_{i:02d}.mp4"
            _run(["ffmpeg", "-y", "-r", "30", "-i", f"{scene_frames}/frame_%04d.png", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(tmp_scene)])
            f.write(f"file '{tmp_scene.name}'\n")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(stitched_video)])

    # 6) TTS
    voice_path = out_dir / "voice.wav"
    script_text = "".join([seg.get("text","") + "\n" for seg in scenes])
    _run(["python", "scripts/tts.py", "--text", script_text, "--out", str(voice_path)])

    # 7) Music
    music_path = out_dir / "music.wav"
    _run(["python", "scripts/musicgen.py", "--style", "uplifting", "--seconds", "60", "--out", str(music_path)])

    # 8) Captions
    srt_path = out_dir / "captions.srt"
    _run(["python", "scripts/captions.py", "--audio", str(voice_path), "--out", str(srt_path)])

    # 9) Compose final
    final_out = out_dir / "final.mp4"
    _run(["python", "scripts/compose.py", "--video", str(stitched_video), "--voice", str(voice_path), "--music", str(music_path), "--srt", str(srt_path), "--out", str(final_out)])

    # 10) Hooks
    hooks_json = out_dir / "hooks.json"
    _run(["python", "scripts/detect_hooks.py", "--video", str(final_out), "--duration", "" + str(int(sum([s.get('duration',3) for s in scenes]))), "--out", str(hooks_json)])
    _run(["python", "scripts/make_hooks.py", "--video", str(final_out), "--timestamps", str(hooks_json), "--outdir", str(out_dir / 'hooks') ])

    # 11) Uploader stubs: placeholder to run uploader scripts if configured
    uploads = []
    for p in platforms:
        # uploader scripts live in uploader/<platform>.py and expect env creds
        up_script = ROOT / "uploader" / f"{p}.py"
        if up_script.exists():
            # Example uploader invocation; uploader will read env vars for credentials
            _run(["python", str(up_script), "--file", str(final_out), "--title", f"{prompt[:80]}", "--description", "Generated by Cinono AI"])
            uploads.append({"platform": p, "status": "uploaded (see uploader logs)"})
        else:
            uploads.append({"platform": p, "status": "no uploader configured"})

    # 12) Write metadata
    meta["final_video"] = str(final_out)
    meta["uploads"] = uploads
    meta_path = out_dir / "meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    print("Job complete. Output:", meta_path)
    return str(meta_path)
