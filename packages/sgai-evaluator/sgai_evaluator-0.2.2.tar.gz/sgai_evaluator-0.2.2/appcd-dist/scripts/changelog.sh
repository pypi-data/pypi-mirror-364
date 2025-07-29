#!/usr/bin/bash

set -e

# this script creates a changelog for component and dist repos based on the .env file
# git commit messages between the version changes(.env) for all the component repos and dist are printed
# the output from this script can be piped to a file and used to update the release notes for the appropriate release in dist repo

# expected directory structure
# .
# ├── appcd-dist <-- this is where this script is present
# ├── iac-gen
# ├── appcd
# ├── appcd-analyzer
# └── appcd-ui

latest_tag=$(git tag --sort=-version:refname  | head -1)
previous_tag=$(git tag --sort=-version:refname  | head -2 | tail -1)

appcd_version_diff=$(git diff "$previous_tag" "$latest_tag" .env | grep -E "^\+APPCD_VERSION|^\-APPCD_VERSION" | awk -F= '{print $2}' | tr '\n' '-' | sed 's/-$//')
iacgen_version_diff=$(git diff "$previous_tag" "$latest_tag" .env | grep -E "^\+IACGEN_VERSION|^\-IACGEN_VERSION" | awk -F= '{print $2}' | tr '\n' '-' | sed 's/-$//')
analyzer_version_diff=$(git diff "$previous_tag" "$latest_tag" .env | grep -E "^\+APPCD_ANALYZER|^\-APPCD_ANALYZER" | awk -F= '{print $2}' | tr '\n' '-' | sed 's/-$//')
ui_version_diff=$(git diff "$previous_tag" "$latest_tag" .env | grep -E "^\+APPCDUI_VERSION|^\-APPCDUI_VERSION" | awk -F= '{print $2}' | tr '\n' '-' | sed 's/-$//')

versions_dict=()
if [ -n "$appcd_version_diff" ]; then
    versions_dict+=("appcd:$appcd_version_diff")
fi
if [ -n "$iacgen_version_diff" ]; then
    versions_dict+=("iac-gen:$iacgen_version_diff")
fi
if [ -n "$analyzer_version_diff" ]; then
    versions_dict+=("appcd-analyzer:$analyzer_version_diff")
fi
if [ -n "$ui_version_diff" ]; then
    versions_dict+=("appcd-ui:$ui_version_diff")
fi

echo "Version Changes:" "${versions_dict[@]}"
echo

for version_diff in "${versions_dict[@]}"; do
    repo=$(echo "$version_diff" | awk -F: '{print $1}')
    version=$(echo "$version_diff" | awk -F: '{print $2}')
    if [ -n "$version" ]; then
        from_version=$(echo "$version" | awk -F'-' '{print $1}')
        to_version=$(echo "$version" | awk -F'-' '{print $2}')
        cd ../"$repo"
        repo_log=$(git log "$from_version".."$to_version" --oneline)

        if [ -n "$repo_log" ]; then          
            echo "## $repo: $from_version -> $to_version"
            echo 
            echo "$repo_log"
            echo
        fi

    fi
done

cd ../appcd-dist
dist_commits=$(git log "$previous_tag".."$latest_tag" --oneline)
if [ -n "$dist_commits" ]; then
    echo 
    echo "## appcd-dist: $previous_tag -> $latest_tag"
    echo
    echo "$dist_commits"
fi

# tags=$(git tag --list --sort=-version:refname --contains "$previous_tag")
# for tag in $tags; do
#     echo
#     echo "### appcd-dist: $tag"
#     git log "$from_version".."$to_version" --oneline
#     gh release view "$tag" --json body | jq -r '.body' | sed 's/^## What'\''s Changed//'
# done
