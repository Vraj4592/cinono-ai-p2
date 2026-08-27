"""Planner: converts the rewritten script (list of scenes) into a simple scenes.json

Input: script.json (produced by scripts/rewriter.py)
Output: scenes.json — list of scenes with text, prompt, duration
"""
import argparse
import json


def main():
    parser = argparse.ArgumentParser("planner")
    parser.add_argument("--script", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.script) as f:
        scenes = json.load(f)
    # Very small planner: pass through but ensure durations and prompts exist
    out = []
    for s in scenes:
        out.append({
            "text": s.get("text",""),
            "prompt": s.get("prompt", s.get("text","")),
            "duration": float(s.get("duration", 3.0))
        })
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print("Wrote scenes to", args.out)

if __name__ == "__main__":
    main()
