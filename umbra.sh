#! /bin/sh
set -eu

log_dir=logs
python="${PYTHON:-python3}"

if ! command -v "$python" > /dev/null; then
    printf 'Python not found (tried "%s")\n' "$python" >&2
    exit 1
fi

log=0
module=UmbraTk

while echo "${1:-}" | grep -E '^(-?-log|-?-text)$' > /dev/null; do
    if [ "${1:-}" = -log ] || [ "${1:-}" = --log ]; then
        log=1
        shift
    fi

    if [ "${1:-}" = -text ] || [ "${1:-}" = --text ]; then
        module=UmbraText
        shift
    fi
done

if [ "$log" -eq 1 ]; then
    log_filename=$(date '+%F-%T%z').log
    log_path="$log_dir"/"$log_filename"

    mkdir -p "$log_dir"
    ln -f -s "$log_filename" "$log_dir"/um.log

    "$python" -O -m umbra."$module" "$@" 2>&1 | tee "$log_path"
else
    "$python" -O -m umbra."$module" "$@"
fi
