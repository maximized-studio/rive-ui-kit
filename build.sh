#!/bin/zsh
# Assembles shared/ + themes/<name>/ into build/<name>/ and verifies it with the Rive CLI.
# A theme file with the same name as a shared file replaces it; anything else is added.
# Usage: ./build.sh [theme ...] [-- extra rive args]   (no theme = all themes)
set -e
cd "${0:A:h}"
RIVE=${RIVE:-$HOME/.rive/bin/rive}
themes=(); extra=()
while (( $# )); do
  [[ $1 == -- ]] && { shift; extra=("$@"); break; }
  themes+=("$1"); shift
done
(( ${#themes} )) || themes=(themes/*(/:t))
for t in $themes; do
  out=build/$t
  rm -rf $out && mkdir -p $out
  cp -R shared/. $out/
  cp -R themes/$t/. $out/ 2>/dev/null || true
  # A palette.json themes the shared Theme Driver (unless the theme forks the driver itself)
  if [[ -f themes/$t/palette.json && ! -f themes/$t/18-ThemeDriver.rml ]]; then
    python3 tools/retheme.py shared/18-ThemeDriver.rml themes/$t/palette.json $out/18-ThemeDriver.rml \
      $out/99-_root.rml $out/99-_root.rml --bake $out
    rm $out/palette.json
  fi
  cat > $out/rive.yaml <<YAML
name: "UI Kit $(tr '[:lower:]' '[:upper:]' <<< ${t:0:1})${t:1}"
main: "Showcase"
logs:
  file: build/rive.log
  problems: build/problems.log
YAML
  # The Rive file this theme pushes to (written by push.sh after the first push)
  [[ -f themes/$t/push.yaml ]] && cat themes/$t/push.yaml >> $out/rive.yaml && rm -f $out/push.yaml
  if [[ -n $PREVIEW ]]; then
    # Local preview only: embed Inter so text renders. Never push a PREVIEW build (custom font blocks Community).
    cp preview-assets/Inter.ttf $out/
    sed -i '' 's|<FontAsset isCustom="false"|<FontAsset file="Inter.ttf" isCustom="false"|' $out/99-_root.rml
  fi
  forks=(themes/$t/*.rml(N:t))
  echo "== $t (forks: ${forks:-none})"
  $RIVE $out --verify $extra
done
