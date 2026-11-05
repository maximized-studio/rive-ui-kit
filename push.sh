#!/bin/zsh
# Builds one theme (never a PREVIEW build) and pushes it to its own Rive file.
# First push creates a NEW file in the kit's project and records it in themes/<theme>/push.yaml.
# Usage: ./push.sh <theme> ["revision label"]
set -e
cd "${0:A:h}"
RIVE=${RIVE:-$HOME/.rive/bin/rive}
t=$1; label=${2:-"build.sh push"}
[[ -n $t && -d themes/$t ]] || { echo "usage: ./push.sh <theme>"; exit 1; }
[[ -z $PREVIEW ]] || { echo "refusing to push a PREVIEW build (custom font blocks Community)"; exit 1; }
PROJECT=1615016   # project of the original "UI starter kit" (workspace Maxmized Studio 663208)
ORIGINAL=1975569  # never push here
grep -q "fileId: $ORIGINAL" themes/$t/push.yaml 2>/dev/null && { echo "themes/$t/push.yaml points at the original file"; exit 1; }
./build.sh $t
out=build/$t
if [[ -f themes/$t/push.yaml ]]; then
  grep -q "^push:" $out/rive.yaml || { echo "build lost the push link; not pushing"; exit 1; }
  $RIVE push $out --yes --name="$label"   # overwrites the linked theme file (never the original)
else
  $RIVE push $out --project=$PROJECT --name="$label"
  sed -n '/^push:/,$p' $out/rive.yaml > themes/$t/push.yaml
  echo "linked: $(cat themes/$t/push.yaml | tr '\n' ' ')"
fi
