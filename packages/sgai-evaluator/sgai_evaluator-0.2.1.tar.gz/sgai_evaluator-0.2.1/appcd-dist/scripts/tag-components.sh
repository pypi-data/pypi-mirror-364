#!/usr/bin/bash

set -e

# this script cd's into each component repo dir
# - checks if the branch is main/master 
# - fetches tags and pulls the latest changes
# - if there are any changes since the last tag, it creates a new patch tag
# - if --release flag is passed, it creates a new gh release

# repos=(appcd iac-gen appcd-analyzer appcd-ui)
repos=(appcd iac-gen appcd-ui) # appcd and analyzer update Changelog.md before tagging a release

usage() {
    echo "Usage: $0 [--release]"
    echo "Optional arguments:"
    echo "  --release   publish gh release"
    exit 1
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --release)
            RELEASE=true
            shift
            ;;
        *)
            usage
            ;;
    esac
done

# assuming appcd-dist is in the same dir as the component repos
cd ../
for repo in "${repos[@]}"; do
    cd "$repo"
    echo Repo: "$repo"
    
    # check if branch is main/master

    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
        echo "Branch is not main, skipping deploy"
        exit 2
    fi
    git fetch --tags > /dev/null
    git pull --rebase > /dev/null
    last_tag=$(git describe --tags --abbrev=0)
    echo "Last tag: $last_tag"

    git --no-pager log "$last_tag"..HEAD --oneline

    
    # if there any changes since last tag, create a new patch tag
    if [ "$RELEASE" = true ] && [ -n "$(git log "$last_tag"..HEAD --oneline)" ]; then
        git --no-pager log "$last_tag"..HEAD --oneline
        echo "Changes found, creating new tag"
        new_tag=$(git describe --tags --abbrev=0 --match "v*.*.*" | awk -F. -v OFS=. '{$NF = $NF + 1;} 1')
        echo "New tag: $new_tag"
        gh release create "$new_tag" -t "$new_tag" --generate-notes
    fi
    cd ../
    echo
done
