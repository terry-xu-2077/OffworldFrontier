# OffworldFrontier — Agent instructions

Before creative work, read [QWEN.md](QWEN.md), [创作/创作方向.md](创作/创作方向.md) and the small [设定/速查索引.md](设定/速查索引.md). NEVER preload all files in `设定/` or the first-season scripts. Use `python scripts/canon_lookup.py route "keywords"`, then `headings PATH` and `read PATH SECTION` for narrowly relevant slices. Default `search` excludes proposal scripts; opt in with `--scope proposals` only when editing that specific work. Character/world/art topics are read on demand. The first-season scripts and event experiments are proposals, not global canon.

Do not restore obsolete movie opening/episode-order requirements; do not replace battery-powered rail minecarts with people pushing heavy carts; do not introduce a second ore lift or mechanical split-flap status board. Keep character dialogue conversational and translate abstract institutional/technical phrases into visible actions.

After edits run: `python scripts/canon_lookup.py check` and `python scripts/check_canon.py`. Inspect warnings manually, especially missing art-image references. The index is a router, not a second source of canon; do not fabricate unseen image assets.
