#!/bin/bash

# --- Ghidorah Node 2 Persistence Setup ---

PLIST_NAME="com.ghidorah.node2.prism.plist"
TARGET_DIR="$HOME/Library/LaunchAgents"
# This script assumes it's run from within the cloned 'node2_config' directory on the Mac
SOURCE_FILE="./${PLIST_NAME}"

# Ensure the target directory exists
mkdir -p "${TARGET_DIR}"

# Check if the source .plist file exists
if [ ! -f "${SOURCE_FILE}" ]; then
    echo "❌ Error: ${SOURCE_FILE} not found. Make sure you are running this script from within the 'node2_config' directory."
    exit 1
fi

# Unload any existing version of the service to ensure a clean start
launchctl unload "${TARGET_DIR}/${PLIST_NAME}" 2>/dev/null
echo "Unloaded existing service (if any)."

# Copy the new .plist file to the LaunchAgents directory
echo "Copying ${PLIST_NAME} to ${TARGET_DIR}..."
cp "${SOURCE_FILE}" "${TARGET_DIR}/"

# Set the correct permissions (important for launchd)
chmod 644 "${TARGET_DIR}/${PLIST_NAME}"
echo "Set permissions for ${PLIST_NAME}."

# Load and start the service
echo "Loading and starting the service..."
launchctl load "${TARGET_DIR}/${PLIST_NAME}"

# Verify the service is running
launchctl list | grep com.ghidorah.node2.prism

echo "✅ Node 2 persistence has been configured. The executor service is now running."
echo "Logs are being written to /tmp/ghidorah_node2.log"
