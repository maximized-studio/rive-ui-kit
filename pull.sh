#!/bin/zsh
# Pulls the current editor file (read-only) and re-splits it into shared/: one .rml per artboard + assets.
# The editor file is the source of truth; run this before committing after editing in Rive.
# Usage: ./pull.sh
set -e
cd "${0:A:h}"
RIVE=${RIVE:-$HOME/.rive/bin/rive}
FILE=1975569
tmp=$(mktemp -d)
trap 'rm -rf $tmp' EXIT
(cd $tmp && $RIVE create kit --from-remote-file=$FILE >/dev/null)
# A file last saved by the editor comes back as one scene.rml; one last pushed from RML comes back
# in the pushed per-artboard layout. Only clear shared/ once the pull really produced one of them.
# (Newer CLIs also drop a tiny scaffold scene.rml next to a per-artboard pull: check that layout first.)
if [[ -s $tmp/kit/99-_root.rml ]]; then
  rm -f shared/*
  cp $tmp/kit/[0-9]*.rml shared/
  cp $tmp/kit/*.luau shared/ 2>/dev/null || true
elif [[ -s $tmp/kit/scene.rml ]] && grep -q '<Artboard ' $tmp/kit/scene.rml; then
  rm -f shared/*
  python3 tools/split.py $tmp/kit/scene.rml shared >/dev/null
  cp $tmp/kit/*.luau shared/ 2>/dev/null || true
else
  echo "pull returned no markup; shared/ left untouched"; exit 1
fi
python3 tools/pull_fixups.py shared
find $tmp/kit -maxdepth 1 -type f \( -name '*.png' -o -name '*.webp' -o -name '*.jpg' -o -name '*.svg' \) -exec cp {} shared/ \;
# Inter is a Rive-hosted font: keep it out of shared/ (PREVIEW builds add it back for local screenshots)
sed -i '' 's|<FontAsset file="[^"]*" |<FontAsset |' shared/99-_root.rml
# Keep the agent skill's component reference in step with the kit
python3 tools/skill_reference.py
./build.sh
