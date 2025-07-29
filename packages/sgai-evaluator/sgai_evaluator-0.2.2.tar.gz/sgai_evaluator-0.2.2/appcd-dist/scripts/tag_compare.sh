#!/bin/bash -eu


KEYS_TO_CHECK=(
    ".appcd.image.tag"
    ".appcd-ui.image.tag"
    ".iac-gen.image.tag"
    ".exporter.helm_workload_5a048be506c75a07b1aeec33d33e56e3.image_tag"
    ".stackgen-vault.helm_workload_54a040c89d8252de9a426f2ad1f92af6.image_tag"
    ".integrations.helm_workload_1b5f1d019692549bb714785b7636f446.image_tag"
    ".infra-catalog-tracker.helm_workload_29510bf8f3775740827eff66846105ef.image_tag"
    ".deployment-manager.helm_workload_eedf62a44e21519893dea9656ef6fc10.image_tag"
)


function usage() {
    echo "Usage: $0 <values_yaml_1> <values_yaml_2>"
    echo "Compares two YAML files image tags values and shows the differences."
    echo "Example: $0 values.yaml values-2.yaml"
}


function main() {
    first_yaml=$1
    second_yaml=$2
    if [ -z "$first_yaml" ] || [ -z "$second_yaml" ]; then
        usage
        exit 1
    fi
    if [ ! -f "$first_yaml" ]; then
        echo "File $first_yaml does not exist."
        exit 1
    fi
    if [ ! -f "$second_yaml" ]; then
        echo "File $second_yaml does not exist."
        exit 1
    fi
    local has_differences=false
    # Extract the image tags from both YAML files
    for key in "${KEYS_TO_CHECK[@]}"; do
        first_value=$(yq -r "$key" "$first_yaml")
        second_value=$(yq -r "$key" "$second_yaml")
        if [ "$first_value" != "$second_value" ]; then
            echo "Difference found for key $key:"
            echo "  $first_yaml: $first_value"
            echo "  $second_yaml: $second_value"
            has_differences=true
        fi
    done
    if [ "$has_differences" = false ]; then
        echo "No differences found."
    fi
    # Check if the first YAML file has all the keys
    for key in "${KEYS_TO_CHECK[@]}"; do
        if ! yq -e "$key" "$first_yaml" > /dev/null; then
            echo "Key $key not found in $first_yaml"
            has_differences=true
        fi
    done
    # Check if the second YAML file has all the keys
    for key in "${KEYS_TO_CHECK[@]}"; do
        if ! yq -e "$key" "$second_yaml" > /dev/null; then
            echo "Key $key not found in $second_yaml"
            has_differences=true
        fi
    done
    if [ "$has_differences" = true ]; then
        echo "Differences found."
        exit 1
    else
        echo "No differences found."
    fi

}


main "$@"
