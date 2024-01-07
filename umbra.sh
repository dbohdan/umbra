#! /bin/sh
set -eu

module=UmbraTk
if [ "${1:-}" = -t ] || [ "${1:-}" = --text ]; then
    module=UmbraText
    shift
fi

log=0
if [ "${1:-}" = -l ] || [ "${1:-}" = --log ]; then
    log=1
    shift
fi

if [ "$log" -eq 1 ]; then
    log_dir=logs
    log_path="$log_dir"/um.log

    mkdir -p "$log_dir"

    if [ -e "$log_path" ]; then
        mv "$log_path" "$log_path"."$(stat -c %Y "$log_path")"
    fi

    python3 -O -m umbra."$module" "$@" 2>&1 | tee "$log_path"
else
    python3 -O -m umbra."$module" "$@"
fi
