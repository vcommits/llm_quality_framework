#!/bin/bash
# Usage: echo "Initiating global audit." | ./vocalize_decoy.sh [sync|decoy]
# Identity: G-Auditor_01 | Strategy: Total Geographic Paradox

MODE=${1:-sync}
VOICE_DIR="$HOME/piper_voices"
PIPER_EXE="$HOME/piper/piper"
OUTPUT_WAV="$HOME/last_vocalization.wav"

# 1. Detect Real-time Geo
COUNTRY_CODE=$(curl -s http://ip-api.com/json/ | grep -o '"countryCode":"[^"]*' | grep -o '[^"]*$')
echo "📍 Current Network Origin: $COUNTRY_CODE"

# 2. Obfuscation Logic (The Paradox Matrix)
if [ "$MODE" == "decoy" ]; then
    echo "🎭 PARADOX MODE ACTIVE: Implementing Signal Mismatch..."
    case $COUNTRY_CODE in
      "AE") # Exiting Dubai
        TARGET_VOICE="ko_KR-goyany-medium" # Project as Korean
        ;;
      "KR") # Exiting Korea
        TARGET_VOICE="el_GR-raphael-medium" # Project as Greek
        ;;
      "TH") # Exiting Thailand
        TARGET_VOICE="fa_IR-amir-medium"   # Project as Farsi
        ;;
      "GR") # Exiting Greece
        TARGET_VOICE="th_TH-pattara-medium" # Project as Thai
        ;;
      "IR") # Exiting Iran/Farsi Region
        TARGET_VOICE="ar_JO-khalid-medium" # Project as Dubai/Gulf Proxy
        ;;
      "CN" | "HK")
        TARGET_VOICE="en_GB-alan-medium"   # Project as UK Academic
        ;;
      *)
        TARGET_VOICE="ro_RO-mihai-medium"  # Default Mismatch: Romanian
        ;;
    esac
else
    # Standard Geo-Sync logic
    case $COUNTRY_CODE in
      "AE") TARGET_VOICE="ar_JO-khalid-medium" ;;
      "KR") TARGET_VOICE="ko_KR-goyany-medium" ;;
      "TH") TARGET_VOICE="th_TH-pattara-medium" ;;
      "IR") TARGET_VOICE="fa_IR-amir-medium" ;;
      "GR") TARGET_VOICE="el_GR-raphael-medium" ;;
      "JP") TARGET_VOICE="ja_JP-hina-medium" ;;
      *) TARGET_VOICE="en_US-lessac-medium" ;;
    esac
fi

MODEL="$VOICE_DIR/$TARGET_VOICE.onnx"

# 3. Execution with Pitch/Speed Randomization
# Randomized 'Voice Fingerprint' prevents acoustic tracking
DRIFT=$(awk -v min=0.92 -v max=1.1 'BEGIN{srand(); print min+rand()*(max-min)}')
echo "🗣️  Projecting Identity: $TARGET_VOICE (Acoustic Drift: $DRIFT)"

if [ -f "$MODEL" ]; then
    $PIPER_EXE --model "$MODEL" --length_scale "$DRIFT" --output_file "$OUTPUT_WAV"
    afplay "$OUTPUT_WAV"
else
    echo "❌ ERROR: Model $TARGET_VOICE not found. Run expansion scripts."
fi