This skill is adapted from Codex CLI's built-in `imagegen` skill
(`~/.codex/skills/.system/imagegen/`), licensed under the Apache License,
Version 2.0 (see `LICENSE.txt`).

Modifications for Claude Code:
- Removed the "built-in tool vs CLI fallback" two-mode design — Claude Code
  has no built-in image tool, so `scripts/image_gen.py` is the only
  execution path.
- `scripts/image_gen.py` and `scripts/remove_chroma_key.py`: docstrings
  updated to drop fallback-mode framing; behavior otherwise unchanged.
- `references/*.md`: reworded to remove dual-mode language and repointed
  paths from `$CODEX_HOME` to this skill's own directory.
- `references/usage.md` replaces the original `references/cli.md` and
  `references/codex-network.md` (network/sandbox notes rewritten for
  Claude Code's permission model instead of Codex's sandbox config).
- Dropped `agents/openai.yaml` and `assets/` (Codex IDE integration
  metadata, not applicable to Claude Code).
- `scripts/_key_store.py` and `scripts/configure_key.py`, and the API-key
  fallback in `image_gen.py`'s `_ensure_api_key()`, are new — not present in
  the original Codex skill. They add local, persisted storage for the user's
  OpenAI key plus a `/image-c` management flow.

---
imagegen · by Marc (marcyy.me)
