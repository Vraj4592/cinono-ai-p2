"""Prompt rewriter: expand a short user prompt into a timed marketing script.

This is a lightweight local rewriter: if a local LLM (transformers) is available it will use it; otherwise it performs a rule-based expansion into a hook -> problem -> solution -> CTA structure with durations.
"""
import argparse
import json
import textwrap
import sys


def rule_expand(prompt):
    # simple marketer template
    hook = prompt.strip()
    problem = f"Are you tired of {hook.lower()}? Here's a quick solution that works." if len(hook)>10 else "Enjoy this quick tip!"
    solution = f"Use {hook} with smart editing and catchy music to increase engagement." 
    cta = "Follow for more tips and try this yourself!"
    scenes = [
        {"text": hook, "prompt": f"Close-up cinematic shot representing: {hook}", "duration": 3},
        {"text": problem, "prompt": f"A frustrated person showing {hook}", "duration": 6},
        {"text": solution, "prompt": f"An elegant demonstration of {hook} solution", "duration": 8},
        {"text": cta, "prompt": f"Bold call-to-action overlay with brand colors", "duration": 3}
    ]
    return scenes


def llm_expand(prompt):
    try:
        from transformers import pipeline
        gen = pipeline('text-generation', model='gpt2')
        out = gen(f"Expand this into a 4-part marketing script with durations: {prompt}", max_length=200, do_sample=False)
        text = out[0]['generated_text']
        # naive split into lines
        parts = [p.strip() for p in text.split('\n') if p.strip()]
        scenes = []
        for i, p in enumerate(parts[:4]):
            scenes.append({"text": p, "prompt": p, "duration": 5})
        return scenes
    except Exception as e:
        print("LLM expansion failed, falling back to rule-based. Error:", e)
        return rule_expand(prompt)


def main():
    parser = argparse.ArgumentParser("rewriter")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    scenes = llm_expand(args.prompt)
    with open(args.out, "w") as f:
        json.dump(scenes, f, indent=2)
    print("Wrote script to", args.out)

if __name__ == "__main__":
    main()
