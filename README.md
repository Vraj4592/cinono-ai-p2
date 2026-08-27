# Cinono AI P2 — End-to-end Open-Source Video Generation PoC

This repository implements an end-to-end, open-source proof-of-concept (PoC) pipeline to:

- Generate or animate images into short videos (Stable Diffusion / img2img pipelines or Ken Burns fallback)
- Generate voiceover (TTS) for scripts
- Generate or include background music
- Combine video, voice, and music into final videos with subtitles
- Auto-detect hook-worthy segments and export short marketing clips
- Provide templates for uploading to social platforms (YouTube/TikTok/Instagram)

IMPORTANT: The earlier "random joke generator" example has been removed by owner request — this repository focuses solely on the Cinono AI video pipeline.

What this repo contains (A → Z):
- README.md (this file)
- .env.example (placeholders for API keys / OAuth tokens)
- requirements.txt (Python dependencies)
- docker-compose.yml (local dev stack: worker + redis)
- scripts/ (main pipeline scripts)
  - tts.py             (TTS wrapper; Coqui preferred / fallback)
  - gen_frames.py      (generate frames via SD or simple Ken Burns)
  - musicgen.py        (MusicGen wrapper / fallback to CC0 track)
  - captions.py        (Whisper/WhisperX wrapper to produce SRT)
  - compose.py         (compose audio/video, burn subtitles)
  - detect_hooks.py    (detect hook timestamps)
  - make_hooks.py      (cut and export hook clips)
- docs/
  - POC_COLAB.md       (how to run the full PoC in Colab — instructions)
- .github/workflows/ci.yml (basic lint/test workflow)

Notes on "free" operation
- Many high-quality components require a GPU. The repo focuses on free/open-source tools and includes a Colab-first flow for users without local GPUs.
- Where heavy models are optional, scripts include fallbacks that run without a GPU for testing and low-res outputs.

License: MIT
