#!/bin/sh
cd C:wd\db\projects\misc\xwing\league\outer-rim-league.github.io
#git checkout
git add .
git commit -am "made changes"
git push -f
read -p "$*"