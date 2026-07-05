---
name: image
description: Generate or edit raster images (photos, illustrations, product/UI mockups, logos, transparent cutouts) via the OpenAI gpt-image-2 API, since Claude Code has no built-in image-generation tool. Use when the user asks to create, generate, draw, mock up, or edit an image, photo, illustration, icon, logo, or transparent-background asset. Also handles `/image-c` requests to set up, view, change, or remove the stored OpenAI API key.
---

# Image Generation Skill

Wraps the OpenAI Images API (`gpt-image-2`, falling back to `gpt-image-1.5` only when needed) in a local script, since Claude Code — unlike Codex — has no built-in `image_gen` tool. This is a single-path skill: every image request goes through `scripts/image_gen.py`.

## Requirements
- An OpenAI API key, from either source (checked in this order): the `OPENAI_API_KEY` env var (session override), or the key stored via `/image-c` in `~/.config/claude-imagegen/config.json` (persists across sessions). See **Setup** below for the first-run flow.
- Python 3 with `openai` and `pillow` installed: `uv pip install openai pillow` (fall back to `pip install openai pillow` if `uv` isn't available).
- Outbound network access to `api.openai.com`.

## Setup (first run)
Before the first `generate`/`edit` call in a fresh session, check configuration once:
```bash
python scripts/configure_key.py status
```
If it reports "Configured: no" and `OPENAI_API_KEY` isn't set either, this is a first-time setup:
1. Tell the user they need an OpenAI API key and link https://platform.openai.com/api-keys.
2. Ask them to paste the key in chat.
3. Store it via stdin, not as a bare CLI arg (avoids it sitting in process listings):
   ```bash
   printf '%s' "<pasted key>" | python scripts/configure_key.py set
   ```
4. Only if the user mentions or implies a third-party relay/proxy service (not official OpenAI) — or the key later fails against the default endpoint — ask for that service's base URL (e.g. `https://xxx.example.com/v1`) and store it too: `python scripts/configure_key.py set --base-url "<url>"`. Don't ask this by default; most users are on the official endpoint.
5. Never echo the key back — not in your response, a dry-run payload, or any log line.
6. Continue with the user's original generate/edit request.

This is a one-time step per machine — later `/image` calls just work without re-asking.

## Reconfiguring the key (`/image-c`)
When the user runs `/image-c`, or asks to view/change/remove/test the stored key or base URL, use `scripts/configure_key.py` — never print the key value in any of these flows:
- View status (also shows the configured base URL, if any): `configure_key.py status`
- Set/replace the key: pipe the new key via stdin (see Setup above)
- Set/replace/clear the base URL (for relay/proxy services): `configure_key.py set --base-url "<url>"` (empty string clears it back to the official endpoint)
- Remove everything: `configure_key.py delete`
- Validate: `configure_key.py validate` (a cheap real API call, not an image generation call — if it fails with something other than a clear auth error, this may be a relay that doesn't support `/v1/models`; suggest trying a real generate call instead)

## Quick start
All script paths below are relative to this skill's own directory (wherever it's installed).
```bash
python scripts/image_gen.py generate --prompt "Test" --out /tmp/test.png --dry-run   # sanity check, no key/network needed
python scripts/image_gen.py generate --prompt "A cozy alpine cabin at dawn" --size 1024x1024 --out output/imagegen/cabin.png
python scripts/image_gen.py edit --image input.png --prompt "Replace only the background with a warm sunset" --out output/imagegen/edit.png
```

## Workflow
1. Make sure a key is configured (see **Setup**) before the first call this session.
2. Decide **generate vs edit**: edit only when the user wants to modify a specific existing local image (pass its path via `--image`); otherwise generate. Claude Code can't hand the script an "attached" image directly — it needs a real file path.
3. Classify the request and build a structured prompt (scene/subject/style/composition/lighting/text/constraints) per `references/prompting.md`, using the taxonomy and recipes in `references/sample-prompts.md`. Normalize already-detailed prompts; only add creative detail to generic ones.
4. Pick model/size/quality from `references/image-api.md` — default `gpt-image-2`, `size auto`, `quality medium`.
5. For transparent backgrounds, use the chroma-key workflow below. Don't switch to `gpt-image-1.5` for true native transparency unless chroma-key removal fails or the user explicitly wants it — ask first either way.
6. Run the script (dry-run first if you want to check the payload), then save the final asset into the current project's workspace, not a scratch/temp directory.
7. For several distinct assets, use `generate-batch` with one job per asset in a JSONL file — don't loop single `generate` calls, and don't use `--n` for anything but variants of one prompt (see `references/usage.md`).
8. Report the saved path(s), the final prompt(s) used, and any model/quality choices that aren't the defaults.

## Transparent images
`gpt-image-2` doesn't support `background=transparent`, so generate on a flat chroma-key background and strip it locally:
```bash
python scripts/image_gen.py generate --prompt "<subject> on a perfectly flat solid #00ff00 background, no shadows, no gradients, crisp edges, generous padding" --out /tmp/imagegen/source.png
python scripts/remove_chroma_key.py --input /tmp/imagegen/source.png --out final.png --auto-key border --soft-matte --transparent-threshold 12 --opaque-threshold 220 --despill
```
Use `#ff00ff` instead of `#00ff00` for green subjects. Validate the result (transparent corners, no color fringe) before shipping it. If the subject is too complex for chroma-key (hair, fur, glass, smoke, reflections), ask before falling back to `--model gpt-image-1.5 --background transparent --output-format png`.

## Guardrails
- Never modify `scripts/image_gen.py` or `scripts/remove_chroma_key.py`; ask the user first if something seems missing.
- Don't write one-off wrapper scripts — call the bundled CLI directly.
- Don't silently switch models away from `gpt-image-2`.
- Reruns fail if the output path already exists; pass `--force` to overwrite, or use a versioned filename instead of clobbering silently.

## Reference map
- `references/prompting.md` — prompt structure, specificity, invariants, transparent-image workflow.
- `references/sample-prompts.md` — use-case taxonomy + copy/paste prompt recipes.
- `references/image-api.md` — model/size/quality parameter reference.
- `references/usage.md` — full CLI reference: flags, batching, masks, output handling, network notes.
- `scripts/image_gen.py` — the CLI (`generate`, `edit`, `generate-batch`).
- `scripts/remove_chroma_key.py` — local chroma-key-to-alpha conversion.
- `scripts/configure_key.py` — `/image-c` backend: `set`, `status`, `delete`, `validate`.
- `NOTICE.md` — provenance: this skill is adapted from Codex CLI's imagegen skill (Apache 2.0).
