#!/bin/bash
# prune.sh

# Path to the config file that will store the previous values
CONFIG_FILE="$HOME/.prune_defaults"

# If the config file exists, load the previous values
if [ -f "$CONFIG_FILE" ]; then
    # shellcheck source=/dev/null
    . "$CONFIG_FILE"
fi

# Prompt the user, using previous values as defaults if they exist
read -e -i "${PERS_USER:-}" -p "What user on the backup server do you need to connect to? " PERS_USER
read -e -i "${PERS_HOSTN:-}" -p "What hostname on the backup server do you need to connect to? " PERS_HOSTN
read -e -i "${HR:-}" -p "How many hourly snapshots should be kept? " HR
read -e -i "${DY:-}" -p "How many daily snapshots should be kept? " DY
read -e -i "${WK:-}" -p "How many weekly snapshots should be kept? " WK
read -e -i "${MN:-}" -p "How many monthly snapshots should be kept? " MN
read -e -i "${YR:-}" -p "How many yearly snapshots should be kept? " YR
read -e -i "${LT:-}" -p "How many of the most recent snapshots should be kept? " LT

# Run the restic command with the provided inputs
sudo restic -r sftp:"$PERS_USER"@"$PERS_HOSTN":/srv/restic-repos/$(hostname) \
    --password-file /root/.restic-password forget --prune \
    --keep-hourly "$HR" --keep-daily "$DY" --keep-weekly "$WK" \
    --keep-monthly "$MN" --keep-yearly "$YR" --keep-last "$LT"

# Save the current settings to the config file for next time
cat <<EOF > "$CONFIG_FILE"
PERS_USER="$PERS_USER"
PERS_HOSTN="$PERS_HOSTN"
HR="$HR"
DY="$DY"
WK="$WK"
MN="$MN"
YR="$YR"
LT="$LT"
EOF
