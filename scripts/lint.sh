#!/bin/bash

# Parse arguments
FIX=false
PROJECT=""
NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX=true
            shift
            ;;
        --p)
            PROJECT="$2"
            shift 2
            ;;
        -t)
            shift
            ;;
        --name)
            NAME="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run ruff with appropriate options
if [ "$FIX" = true ]; then
    ruff check --fix "$NAME"
    ruff format "$NAME"
else
    ruff check "$NAME"
fi
