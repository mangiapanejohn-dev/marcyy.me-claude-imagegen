# CLI usage reference (`scripts/image_gen.py`)

This is the skill's only execution path — there is no built-in tool to fall back from. `generate-batch` is a subcommand of this same script, not a separate mode; the word "batch" in a request does not imply anything special.

## What this CLI does
- `generate`: generate a new image from a prompt
- `edit`: edit one or more existing local images (Claude Code has no way to read an "attached" image directly into this script — always pass a real file path via `--image`)
- `generate-batch`: run many generation jobs from a JSONL file (one job per distinct asset)

Real API calls require **network access** + `OPENAI_API_KEY`. `--dry-run` needs neither.

## Quick start
```bash
export IMAGE_GEN=scripts/image_gen.py
```

Dry-run (prints the API payload and resolved output path; no network, no `openai` package needed):
```bash
python "$IMAGE_GEN" generate --prompt "Test" --out output/imagegen/test.png --dry-run
```

Generate (requires `OPENAI_API_KEY` + network):
```bash
python "$IMAGE_GEN" generate \
  --prompt "A cozy alpine cabin at dawn" \
  --size 1024x1024 \
  --out output/imagegen/alpine-cabin.png
```

Edit:
```bash
python "$IMAGE_GEN" edit \
  --image input.png \
  --prompt "Replace only the background with a warm sunset" \
  --out output/imagegen/sunset-edit.png
```

## Guardrails
- Run the bundled script directly (`python "$IMAGE_GEN" ...`); don't write one-off wrapper scripts unless the user explicitly asks for a custom wrapper.
- **Never modify** `scripts/image_gen.py` or `scripts/remove_chroma_key.py`. If something is missing, ask the user before doing anything else.
- Don't silently switch models away from `gpt-image-2`; ask first (see Transparent backgrounds in `references/image-api.md`), unless the user already explicitly requested `gpt-image-1.5`.

## Defaults
- Model: `gpt-image-2`
- Size: `auto`
- Quality: `medium`
- Output format: `png`
- Default one-off output path: `output/imagegen/output.png`
- Background: unspecified unless `--background` is set

## gpt-image-2 size and model guidance
- Use `--quality low` for fast drafts, thumbnails, and quick iterations.
- Use `--quality medium`, `--quality high`, or `--quality auto` for final assets, dense text, diagrams, identity-sensitive edits, and high-resolution outputs.
- Square images are typically fastest. Use `--size 1024x1024` for quick square drafts.
- For 4K-style output, use `--size 3840x2160` (landscape) or `--size 2160x3840` (portrait).
- Do not pass `--input-fidelity` with `gpt-image-2`; this model always uses high fidelity for image inputs.
- Do not use `--background transparent` with `gpt-image-2` — use the chroma-key workflow instead (see `references/prompting.md`), or ask before switching to `gpt-image-1.5`.

Popular `gpt-image-2` sizes: `1024x1024`, `1536x1024`, `1024x1536`, `2048x2048`, `2048x1152`, `3840x2160`, `2160x3840`, `auto`.

Size constraints: max edge `<= 3840px`; both edges multiples of `16px`; long:short ratio `<= 3:1`; total pixels between `655,360` and `8,294,400`.

## Quality, input fidelity, and masks
- `--quality` works for `generate`, `edit`, and `generate-batch`: `low|medium|high|auto`
- `--input-fidelity` is **edit-only**, validated as `low|high`; not supported for `gpt-image-2`
- `--mask` is **edit-only**

```bash
python "$IMAGE_GEN" edit \
  --model gpt-image-1.5 \
  --image input.png \
  --prompt "Change only the background" \
  --quality high \
  --input-fidelity high \
  --out output/imagegen/background-edit.png
```

Mask notes:
- For multi-image edits, pass repeated `--image` flags; order is meaningful, so describe each image by index and role in the prompt.
- Image and mask must be the same size/format, each under 50MB, and the mask needs an alpha channel.
- If multiple input images are provided, the mask applies to the first image.
- Masking is prompt-guided, not pixel-perfect.
- Repeat invariants in edit prompts (`change only the background; keep the subject unchanged`) to reduce drift across iterations.

## Output handling
- Use `tmp/imagegen/` for temporary JSONL inputs or scratch files; clean them up when done.
- Save final assets under the current project's workspace (e.g. `output/imagegen/` or wherever the project keeps generated assets) — never leave a project-bound asset only in a scratch/temp directory.
- Reruns fail if a target file already exists unless you pass `--force`; prefer a versioned filename (`hero-v2.png`) over silently overwriting.
- `--out-dir` changes one-off naming to `image_1.<ext>`, `image_2.<ext>`, etc.
- Downscaled copies use the default suffix `-web` unless overridden with `--downscale-suffix`.

## Common recipes

Generate with augmentation fields:
```bash
python "$IMAGE_GEN" generate \
  --prompt "A minimal hero image of a ceramic coffee mug" \
  --use-case "product-mockup" \
  --style "clean product photography" \
  --composition "wide product shot with usable negative space for page copy" \
  --constraints "no logos, no text" \
  --out output/imagegen/mug-hero.png
```

Generate + a downscaled copy for fast web loading:
```bash
python "$IMAGE_GEN" generate \
  --prompt "A cozy alpine cabin at dawn" \
  --size 1024x1024 \
  --downscale-max-dim 1024 \
  --out output/imagegen/alpine-cabin.png
```

Generate multiple distinct assets concurrently (async batch):
```bash
mkdir -p tmp/imagegen output/imagegen/batch
cat > tmp/imagegen/prompts.jsonl << 'EOF'
{"prompt":"Cavernous hangar interior with a compact shuttle parked near the center","use_case":"stylized-concept","composition":"wide-angle, low-angle","lighting":"volumetric light rays through drifting fog","constraints":"no logos or trademarks; no watermark","size":"1536x1024"}
{"prompt":"Gray wolf in profile in a snowy forest","use_case":"photorealistic-natural","composition":"eye-level","constraints":"no logos or trademarks; no watermark","size":"1024x1024"}
EOF

python "$IMAGE_GEN" generate-batch \
  --input tmp/imagegen/prompts.jsonl \
  --out-dir output/imagegen/batch \
  --concurrency 5

rm -f tmp/imagegen/prompts.jsonl
```

Notes:
- `generate-batch` requires `--out-dir`.
- Use `--concurrency` to control parallelism (default `5`).
- Per-job overrides supported in JSONL: `size`, `quality`, `background`, `output_format`, `output_compression`, `moderation`, `n`, `model`, `out`, and prompt-augmentation fields.
- `--n` generates variants of a single prompt; `generate-batch` is for many different prompts — don't substitute one for the other.

## Network access
Real generate/edit calls need outbound HTTPS to `api.openai.com`. If a Bash call fails or hangs because network access isn't permitted in the current environment, tell the user network access is required and ask them to allow it (or run the command themselves) rather than retrying blindly.

## See also
- `references/image-api.md` — model/size/quality/parameter reference.
- `references/prompting.md` — prompt structure and transparent-image workflow.
- `references/sample-prompts.md` — copy/paste prompt recipes.
