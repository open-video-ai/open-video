#!/usr/bin/env bash
# Publish v0.0.1 Hub cards to open-video-ai/* (requires org write token).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
ORG="${HF_ORG:-open-video-ai}"
VER="${OPEN_VIDEO_VERSION:-0.0.1}"

echo "Target org: $ORG  version: $VER"
echo "Requires: hf auth with write access to $ORG"

hf repos create "$ORG/open-video" --type model --public --exist-ok
hf upload "$ORG/open-video" "$ROOT/open-video/README.md" README.md --repo-type model \
  --commit-message "docs: OpenVideo v${VER} software card"
hf upload "$ORG/open-video" "$ROOT/open-video/VERSION" VERSION --repo-type model \
  --commit-message "chore: VERSION ${VER}"
hf upload "$ORG/open-video" "$ROOT/open-video/CITATION.cff" CITATION.cff --repo-type model \
  --commit-message "chore: CITATION.cff"

hf repos create "$ORG/open-video-prompts" --type dataset --public --exist-ok
hf upload "$ORG/open-video-prompts" "$ROOT/open-video-prompts/README.md" README.md --repo-type dataset \
  --commit-message "docs: prompts dataset v${VER}"
hf upload "$ORG/open-video-prompts" "$ROOT/open-video-prompts/prompts" prompts --repo-type dataset \
  --commit-message "data: prompt recipes v${VER}"

hf repos tag create "$ORG/open-video" "v${VER}" -m "OpenVideo ${VER}" || true
echo "Done: https://huggingface.co/$ORG/open-video"
