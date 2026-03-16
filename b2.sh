#!/bin/bash

WORK_DIR="/path/to/input"

process_file() {
    local file="$1"
    echo "Processing file: $file"

    # Example command (replace with your real one)
    ./first_command.sh "$file"
    return $?
}

success_action() {
    local file="$1"
    echo "Success action for: $file"

    # Example next step
    ./second_command.sh "$file"
}

cd "$WORK_DIR" || exit 1

for file in *; do
    [[ -f "$file" ]] || continue

    process_file "$file"
    rc=$?

    if [[ $rc -eq 0 ]]; then
        success_action "$file"
    else
        echo "Failed processing $file (rc=$rc)"
    fi
done
