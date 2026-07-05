# claude-imagegen

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE.txt)
[![Python 3](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/)
[![Works with Claude Code](https://img.shields.io/badge/works%20with-Claude%20Code-D97757.svg)](https://code.claude.com)

**Give [Claude Code](https://code.claude.com) image-generation superpowers** — generate and edit real images without ever leaving the conversation.

You're mid-session with Claude Code, building a landing page or an app, and
you need a hero image, an icon, or a product shot with the background swapped
out. Claude can write the code around it, but it can't make the image itself
— so you tab away to a web-based image tool, generate something, download it,
then drag it back into your project. This skill closes that gap: ask for the
image in the same conversation, and it lands in your project as a file,
ready to use.

If you're just browsing the Claude Code skills ecosystem: this is also a
working example of a fairly complete skill — CLI scripts, local persisted
config, a `/image-c` sub-flow, structured prompt guidance — if you're
building your own.

| Plain generate | Transparent cutout |
| --- | --- |
| ![A matte ceramic mug on a wood table](examples/generate.png) | ![A potted succulent, background removed](examples/cutout-transparent.png) |

## Before / after

| | Without this skill | With this skill |
| --- | --- | --- |
| Get an image | Switch to a separate web tool, write the prompt again there, download, drag the file into your project | Ask Claude for it, in the same conversation |
| Transparent cutout | Manually background-remove in another app | Automatic chroma-key generate + local removal |
| Iterate | Re-describe the whole thing each time | Claude re-prompts with your existing constraints preserved |

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

---

Found this useful? A star helps other people find it. Bug reports and PRs are welcome too.
