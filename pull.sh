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
rm -f shared/*
python3 tools/split.py $tmp/kit/scene.rml shared >/dev/null
find $tmp/kit -maxdepth 1 -type f \( -name '*.png' -o -name '*.webp' -o -name '*.jpg' -o -name '*.svg' \) -exec cp {} shared/ \;
# Inter is a Rive-hosted font: keep it out of shared/ (PREVIEW builds add it back for local screenshots)
sed -i '' 's|<FontAsset file="[^"]*" |<FontAsset |' shared/99-_root.rml
./build.sh
