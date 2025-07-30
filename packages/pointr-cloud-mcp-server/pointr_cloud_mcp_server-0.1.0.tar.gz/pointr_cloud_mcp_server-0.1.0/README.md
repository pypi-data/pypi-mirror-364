# Pointr Indoor Location Assistant

This project provides an indoor location assistant powered by the Pointr MCP server. Users can interact with the assistant to get QR code links for directions to specific places or categories (e.g., toilets, restaurants, cafes, entertainment centers) within a venue.

## Features
- Find directions to specific points of interest (POIs) or general categories.
- Generate QR codes for navigation.
- Uses Pointr MCP server for location logic.
- Logs client identifiers and actions to `pointr_agent.log`.

## Usage
1. **Setup Environment**
   - Ensure Python 3.13+ is installed.
   - Install dependencies from `requirements.txt`:
     ```bash
     pip install -r requirements.txt
     ```
   - Configure environment variables in `.env` or via VS Code settings (see `settings.json`).

2. **Run the MCP Server**
   - Start the server:
     ```bash
     python PointrAgent.py
     ```
   - Or use the VS Code MCP integration as configured in `settings.json`.

3. **Interact with the Assistant**
   - Ask for directions (e.g., "Where is the nearest cafe?", "How can I go to the meeting room?").
   - The assistant will respond with a QR code link for navigation.

## File Structure
- `PointrAgent.py`: Main agent logic and MCP tool definitions.
- `app.py`: Example runner for the agent.
- `requirements.txt`: Python dependencies.
- `pointr_agent.log`: Log file for client identifiers and actions.
- `settings.json`: VS Code and MCP server configuration.

## MCP Tools
- `find_exact_poi_from_user_input`: Extracts POI ID from user input.
- `find_exact_category_from_user_input`: Extracts category from user input.
- `generate_qr_code_for_specific_poi`: Generates QR code for a specific POI.
- `generate_qr_code_for_category`: Generates QR code for a category.

## Environment Variables
- `PC_API_URL`: Pointr API endpoint.
- `PC_CLIENT_ID`: Client identifier.
- `PC_CLIENT_SECRET`: Client secret.

## Logging
All client identifiers and tool actions are logged to `pointr_agent.log` for debugging and audit purposes.

## License
MIT
