#!/bin/sh -ex

# StackGen releases URL
RELEASES_URL="https://stackgen:user@releases.stackgen.com/appcd-dist/"
LATEST_FILE_URL="${RELEASES_URL}latest.txt"

download_zip_latest() {
    local latest_zip_file="stackgen-latest.zip"
    echo "Downloading the latest zip file..."
    # Check if a zip file name was found
    curl -O "${RELEASES_URL}${latest_zip_file}"

    # Unzip the file into the stackgen directory
    unzip "${latest_zip_file}" -d stackgen
}

start_stackgen() {
    # Change to the stackgen directory
    cd stackgen

    # Execute the setup.sh script
    if [ ! -f "setup.sh" ]; then
        echo "setup.sh not found in the extracted directory."
        exit 1
    fi
    chmod +x setup.sh
    ./setup.sh
}

main() {
    # Create the stackgen directory
    mkdir -p stackgen

    ## Download the latest zip file
    download_zip_latest

    ## Start stackgen
    #  ask for user confirmation
    echo "Do you want to start stackgen? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        echo "You can always run stackgen by executing the setup.sh from stackgen directory."
        exit 0
    fi

    start_stackgen
}

main
