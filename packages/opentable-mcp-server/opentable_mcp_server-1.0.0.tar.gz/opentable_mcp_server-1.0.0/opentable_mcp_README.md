# OpenTable MCP Server

An MCP (Model Context Protocol) server that provides natural language access to OpenTable restaurant reservation functionality. This server uses the published `opentable-rest-client` package to interact with the OpenTable REST API.

## Features

- 🔍 **Restaurant Search**: Find restaurants by location and cuisine
- 📅 **Availability Check**: Get real-time availability for any restaurant  
- 📝 **Reservation Management**: Book, cancel, and list reservations
- 💳 **Payment Integration**: Add credit cards for reservations requiring them
- 👤 **User Management**: Register test users for development
- 🏥 **Health Monitoring**: Check API service status

## Installation

### Option 1: Using uvx (Recommended)

The easiest way to use this MCP server is with `uvx`:

```bash
uvx opentable-mcp-server
```

### Option 2: Using pip

```bash
pip install opentable-mcp-server
opentable-mcp-server
```

### Option 3: Development Installation

```bash
git clone https://github.com/wheelis/opentable_mcp.git
cd opentable_mcp
pip install -e .
opentable-mcp-server
```

## Claude Desktop Configuration

Add the server to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json`):

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

**Alternative with pip:**
```json
{
  "mcpServers": {
    "opentable": {
      "command": "opentable-mcp-server",
      "env": {
        "OPENTABLE_ORG_KEY": "your-org-key-here"
      }
    }
  }
}
```

Restart Claude Desktop after updating the configuration.

## Usage

Once configured, you can interact with OpenTable through natural language in Claude Desktop:

### Getting Started
```
"Register me for OpenTable with name John Doe and phone 5551234567"
```

### Restaurant Search
```
"Find Italian restaurants in New York City"
"Search for Le Bernardin in Manhattan"
"Show me seafood restaurants in Vancouver for 4 people"
```

### Check Availability
```
"Check availability for restaurant ID 12345 for tomorrow evening"
"What times are available at restaurant 67890 for 2 people this week?"
```

### Make Reservations
```
"Book a table at restaurant 12345 for tomorrow at 7pm for 2 people"
"Make a reservation with special request for a window table"
```

### Manage Reservations
```
"Show me my current reservations"
"Cancel reservation 101750"
```

### Payment Management
```
"Add my credit card for reservations"
```

## Available Tools

The MCP server exposes these tools to Claude:

- `register_user` - Register a new test user account
- `health_check` - Check API service status
- `search_restaurants` - Find restaurants by location/cuisine
- `get_availability` - Get available time slots for a restaurant
- `book_reservation` - Book a restaurant reservation
- `list_reservations` - List all user reservations
- `cancel_reservation` - Cancel an existing reservation
- `add_credit_card` - Add payment method (real accounts only)

## Configuration

### Environment Variables

- `OPENTABLE_ORG_KEY`: Your organization key for API access (optional, has default)

### API Limitations

- **Test Accounts**: Created via `register_user()` are suitable for development but have limitations:
  - ✅ Can search restaurants and check availability
  - ✅ Can book at restaurants not requiring credit cards
  - ✅ Can manage and cancel reservations
  - ❌ Cannot add credit cards or book at card-required restaurants

- **Real Accounts**: Full functionality including credit card management

## Error Handling

The server provides comprehensive error handling with helpful messages:

```json
{
  "success": false,
  "error": "Please register a user first using register_user()",
  "details": "Additional context when available"
}
```

## Development

### Running Locally

```bash
git clone https://github.com/wheelis/opentable_mcp.git
cd opentable_mcp
pip install -e .
python opentable_mcp_server.py
```

The server runs on stdio transport and communicates via JSON-RPC with MCP clients.

### Testing

Test individual functions by using Claude Desktop or any MCP client. Start with:

1. Register a user: `register_user("John", "Doe", "5551234567")`
2. Check health: `health_check()`
3. Search restaurants: `search_restaurants("New York, NY")`

## Architecture

```
Claude Desktop (MCP Host)
    ↓ JSON-RPC over stdio
OpenTable MCP Server (Python)
    ↓ HTTP REST API calls
opentable-rest-client package
    ↓ HTTPS
OpenTable REST API Service
```

## Troubleshooting

### Server Not Showing Up
1. Ensure `uvx` or the package is installed
2. Check Claude Desktop configuration syntax
3. Verify environment variables are set
4. Restart Claude Desktop

### Tool Calls Failing
1. Check if user is registered first
2. Verify org key is correct
3. Check Claude Desktop logs: `~/Library/Logs/Claude/mcp*.log`

### Import Errors
```bash
pip install --upgrade opentable-mcp-server
```

## Support

- **MCP Protocol**: [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- **OpenTable Client**: [PyPI Package](https://pypi.org/project/opentable-rest-client/)
- **Issues**: Create GitHub issues for bugs or feature requests

## License

MIT License - see LICENSE file for details. 