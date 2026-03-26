#!/bin/bash

# Windsurf Automation Script
# Opens new Windsurf window, starts chat, and passes prompt for recommendations

set -e

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROMPT_FILE="${1:-workflow/generated_prompt.txt}"
APP_NAME="${2:-unknown_app}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Windsurf Automation Script ===${NC}"
echo -e "${GREEN}Project Directory: ${PROJECT_DIR}${NC}"
echo -e "${GREEN}Prompt File: ${PROMPT_FILE}${NC}"
echo -e "${GREEN}App Name: ${APP_NAME}${NC}"
echo ""

# Check if prompt file exists
if [ ! -f "${PROJECT_DIR}/${PROMPT_FILE}" ]; then
    echo -e "${YELLOW}Error: Prompt file not found at ${PROJECT_DIR}/${PROMPT_FILE}${NC}"
    exit 1
fi

# Read the prompt
PROMPT_CONTENT=$(cat "${PROJECT_DIR}/${PROMPT_FILE}")

echo -e "${BLUE}Step 1: Opening new Windsurf window...${NC}"

# For macOS - Open new Windsurf window with the project
# Note: Adjust the application name if Windsurf has a different name
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open -na "Windsurf" --args "${PROJECT_DIR}"
    sleep 3  # Wait for window to open
    
    echo -e "${BLUE}Step 2: Activating Windsurf window...${NC}"
    osascript -e 'tell application "Windsurf" to activate'
    sleep 1
    
    echo -e "${BLUE}Step 3: Opening new chat (Cmd+L)...${NC}"
    # Send Cmd+L to open new chat
    osascript -e 'tell application "System Events" to keystroke "l" using command down'
    sleep 2
    
    echo -e "${BLUE}Step 4: Pasting prompt into chat...${NC}"
    # Copy prompt to clipboard
    echo "${PROMPT_CONTENT}" | pbcopy
    
    # Paste into chat (Cmd+V)
    osascript -e 'tell application "System Events" to keystroke "v" using command down'
    sleep 1
    
    echo -e "${GREEN}✓ Prompt pasted into Windsurf chat!${NC}"
    echo -e "${YELLOW}Please review the prompt and press Enter in Windsurf to submit.${NC}"
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo -e "${YELLOW}Linux automation not fully implemented yet.${NC}"
    echo -e "${YELLOW}Please manually:${NC}"
    echo "1. Open Windsurf"
    echo "2. Press Ctrl+L for new chat"
    echo "3. Paste the prompt from: ${PROMPT_FILE}"
    
else
    # Windows (Git Bash/WSL)
    echo -e "${YELLOW}Windows automation not fully implemented yet.${NC}"
    echo -e "${YELLOW}Please manually:${NC}"
    echo "1. Press Ctrl+Shift+N to open new Windsurf window"
    echo "2. Press Ctrl+L for new chat"
    echo "3. Paste the prompt from: ${PROMPT_FILE}"
fi

echo ""
echo -e "${BLUE}=== Next Steps ===${NC}"
echo "1. Review the prompt in Windsurf chat"
echo "2. Press Enter to submit and generate recommendations"
echo "3. Wait for AI to generate the recommendations.py file"
echo "4. The recommendations will be saved automatically"
echo ""
echo -e "${GREEN}Prompt file location: ${PROJECT_DIR}/${PROMPT_FILE}${NC}"
