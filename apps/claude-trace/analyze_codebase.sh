#!/bin/bash

# Using Claude Code to analyze the codebase by recursively reading through the entire codebase from bottom to top.
# For each directory, a CLAUDE.md file will be created or modified with a summary.
# If a subdirectory exists, its CLAUDE.md will be read first before analyzing the directory itself.

# Default folder name with timestamp if not provided
folder_name="analysis-$(date +%Y%m%d-%H%M%S)"

while getopts "f:" opt; do
    case $opt in
        f)
            folder_name="$OPTARG"
            ;;
        \?)
            echo "Usage: $0 [-f folder_name]"
            echo "  -f: Name of the folder to create under .claude-trace/ (default: analysis-TIMESTAMP)"
            exit 1
            ;;
    esac
done

# Create the logs directory under .claude-trace/
logs_dir=".claude-trace/$folder_name"
mkdir -p "$logs_dir"
echo "Created logs directory: $logs_dir"

cleanup() {
    echo "Ctrl-C detected. Exiting..."
    exit 0
}

trap cleanup INT

directories_to_analyze=$(fd --type d --hidden --exclude .git --exclude .claude | sort -r)
directories_to_analyze+=(".")


echo "Directories to analyze:
$directories_to_analyze
"

for i in $directories_to_analyze; do
    echo "Documenting directory: $i"
    # Replace '/' with '-' in the directory path for log file name
    sanitized_dir=$(echo $i | tr '/' '-')
    # Remove leading dash if present
    sanitized_dir=${sanitized_dir#-}
    # Remove trailing dash if present
    sanitized_dir=${sanitized_dir%-}
    # Use default name if sanitized_dir is empty (for root directory)
    if [ -z "$sanitized_dir" ]; then
        sanitized_dir="root"
    fi
    
    claude-trace --log "$sanitized_dir" --no-open --run-with -p "@agent-directory-documenter Document the directory: $i"> /dev/null 2>&1

    mv "./.claude-trace/$sanitized_dir.*" "$logs_dir"
    echo "  Log file: $logs_dir/$sanitized_dir.{jsonl,html}"
done

claude-trace --log "root" --no-open --run-with -p "@agent-directory-documenter Document the directory: ./ and ignore $0 file"> /dev/null 2>&1
mv "./.claude-trace/root.*" "$logs_dir"

echo "\nAnalysis complete! Logs are stored in: $logs_dir/"