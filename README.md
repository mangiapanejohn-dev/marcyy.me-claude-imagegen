# claude-imagegen

Give [Claude Code](https://code.claude.com) image-generation superpowers.

Claude Code has no built-in tool for creating or editing images. This skill
adds one: generate photos, illustrations, product/UI mockups, logos, and
transparent-background cutouts, right from a normal conversation — no extra
app, no manual scripting.

| Plain generate | Transparent cutout |
| --- | --- |
| ![A matte ceramic mug on a wood table](examples/generate.png) | ![A potted succulent, background removed](examples/cutout-transparent.png) |

## Install

```bash
npx skills add mangiapanejohn-dev/marcyy.me-claude-imagegen
```

Or clone it straight into Claude Code's user-level skills directory:

```bash
git clone https://github.com/mangiapanejohn-dev/marcyy.me-claude-imagegen.git ~/.claude/skills/image
```

Once installed, just ask Claude Code to generate or edit an image — it picks
up the skill automatically. `/image-c` manages the stored API key.

## What it does

- **Generate** — photos, illustrations, product shots, UI/app mockups, logos, diagrams
- **Edit** — modify an existing local image (background swap, object removal, relighting, etc.)
- **Batch** — generate many distinct assets concurrently from one JSONL file
- **Transparent cutouts** — chroma-key generate + local background removal (no native transparent-output model required)

See [`SKILL.md`](SKILL.md) and [`references/`](references) for the full
prompting and usage guide Claude follows.

## Requirements

- An OpenAI API key (official, or a third-party OpenAI-compatible relay/proxy
  service — both are supported, see **Setup** below).
- Python 3 with `openai` and `pillow`: `uv pip install openai pillow` (or `pip install openai pillow`).
- Outbound network access to the API endpoint you configure.

**Disclosure:** this skill is a wrapper around OpenAI's Images API
(`gpt-image-2`, falling back to `gpt-image-1.5` only for true transparent
output). Your prompts and generated images are sent to whichever endpoint
you configure (OpenAI directly, or your chosen relay/proxy), governed by
that provider's terms and pricing — not Anthropic's.

## Setup

The first time you ask Claude Code to generate an image, it'll check for a
configured key and walk you through pasting one if none is found. That's
stored locally at `~/.config/claude-imagegen/config.json` (mode `600`, never
committed to git) and reused for every future session — a one-time step per
machine.

If you use a third-party relay/proxy instead of the official OpenAI
endpoint, tell Claude its base URL (e.g. `https://xxx.example.com/v1`) and
it'll store that alongside the key.

Manage it any time with `/image-c`:
- view status — `python scripts/configure_key.py status`
- change the key/base URL — `python scripts/configure_key.py set --key ... --base-url ...`
- remove everything — `python scripts/configure_key.py delete`
- test it works — `python scripts/configure_key.py validate`

## License

Apache License 2.0 — see [`LICENSE.txt`](LICENSE.txt). This skill is adapted
from Codex CLI's built-in `imagegen` skill; see [`NOTICE.md`](NOTICE.md) for
what changed.
