# OpenTable MCP Server

An MCP (Model Context Protocol) server that provides natural language access to OpenTable restaurant reservation functionality.

## 🚀 **One-Step Setup**

**No installation required!** Just configure Claude Desktop:

### 1. Add to Claude Desktop Configuration

Add this to your Claude Desktop configuration file (`~/.claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "opentable": {
      "command": "uvx",
      "args": ["opentable-mcp-server"],
      "env": {
        "OPENTABLE_ORG_KEY": "your-org-key-here"
      }
    }
  }
}
```

### 2. Restart Claude Desktop

### 3. Start using natural language:
```
"Register me for OpenTable and find Italian restaurants in NYC"
```

**That's it!** `uvx` automatically downloads and installs the MCP server when Claude Desktop starts.

---

## Features

- 🔍 **Restaurant Search**: Find restaurants by location and cuisine
- 📅 **Availability Check**: Get real-time availability for any restaurant  
- 📝 **Reservation Management**: Book, cancel, and list reservations
- 💳 **Payment Integration**: Add credit cards for reservations requiring them
- 👤 **User Management**: Register test users for development
- 🏥 **Health Monitoring**: Check API service status

## Installation

### **Recommended: Claude Desktop Auto-Install**

The easiest way is to let Claude Desktop handle everything automatically. Just add the configuration above to `~/.claude_desktop_config.json` and restart Claude Desktop.

When Claude Desktop starts, `uvx` will:
- ✅ Automatically download `opentable-mcp-server` from PyPI
- ✅ Install all dependencies including `opentable-rest-client`
- ✅ Create an isolated environment
- ✅ Start the MCP server

### Alternative: Manual Installation

If you prefer to install manually first:

```bash
# Option 1: Using uvx
uvx opentable-mcp-server

# Option 2: Using pip
pip install opentable-mcp-server
```

## Configuration

### Claude Desktop Configuration

**Already shown above!** The configuration in the "One-Step Setup" section is all you need.

For reference, the configuration file locations are:
- **macOS**: `~/.claude_desktop_config.json` or `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

See `claude_desktop_config_example.json` in this directory for a complete example.

### Environment Variables

- `OPENTABLE_ORG_KEY` (required): Your OpenTable organization key

## Project Structure

```
mcp/
├── opentable_mcp_server.py    # Main MCP server implementation
├── setup.py                   # Package setup configuration
├── requirements.txt           # Python dependencies
├── MANIFEST.in               # Package manifest
├── opentable_mcp_README.md   # This documentation
├── claude_desktop_config_example.json  # Example configuration
└── dist/                     # Built packages
```

## Available Tools

The MCP server provides these tools for natural language interaction:

### Restaurant Discovery
- **search_restaurants**: Find restaurants by location, cuisine, and preferences
- **get_restaurant_availability**: Check real-time availability for a specific restaurant
- **get_restaurant_timeslots**: Get available time slots for a restaurant

### Reservation Management  
- **book_reservation**: Make a new reservation
- **cancel_reservation**: Cancel an existing reservation
- **list_reservations**: View user's current reservations
- **modify_reservation**: Change an existing reservation

### User & Payment
- **register_user**: Create a new user account (for testing)
- **get_user_info**: Get current user information
- **add_credit_card**: Add a payment method
- **list_credit_cards**: View saved payment methods

### Monitoring
- **health_check**: Check API service status

## Publishing to PyPI

To publish the MCP server package:

```bash
cd mcp/

# Build the package
python -m build

# Upload to PyPI (requires authentication)
twine upload dist/*
```

## Development

### Testing the Server

```bash
cd mcp/
python opentable_mcp_server.py
```

The server will start and listen for MCP protocol messages via stdio.

### Dependencies

- `mcp>=1.2.0`: Model Context Protocol framework
- `opentable-rest-client>=1.0.0`: Published OpenTable API client

## License

MIT License - see the main project repository for details.

## Contributing

Contributions are welcome! Please see the main project repository at https://github.com/wheelis/opentable_mcp 