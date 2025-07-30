# KSEI MCP Server

A Model Context Protocol (MCP) server that provides access to KSEI (Kustodian Sentral Efek Indonesia) portfolio data through Claude Desktop and other MCP clients.

## Features

- **Portfolio Management**: Access portfolio summary, asset breakdown, and total values
- **Cash Balances**: View cash balances across all registered accounts
- **Holdings Data**: Retrieve equity, mutual fund, and bond holdings with current valuations
- **Account Information**: Access global identity and account details
- **Secure Authentication**: Environment-based credential management with token caching
- **Auto-configuration**: Automatic client setup on server startup

## Installation

### Prerequisites

- Python 3.11+
- KSEI account credentials
- MCP-compatible client (Claude, Copilot, Gemini CLI)

### Setup

1. **Clone or download the files**:
   ```bash
   mkdir ksei-mcp && cd ksei-mcp
   # Copy ksei_mcp.py and ksei_client.py to this directory
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure credentials** (choose one method):

   **Method A: Environment Variables**
   ```bash
   export KSEI_USERNAME="your-email@domain.com"
   export KSEI_PASSWORD="your-password"
   export KSEI_AUTH_PATH="~/.cache/ksei-mcp/auth"
   ```

   **Method B: .env File**
   ```bash
   # Create .env file in project directory
   echo "KSEI_USERNAME=your-email@domain.com" > .env
   echo "KSEI_PASSWORD=your-password" >> .env
   echo "KSEI_AUTH_PATH=~/.cache/ksei-mcp/auth" >> .env
   ```

   **Method C: Configuration File**
   ```bash
   mkdir -p ~/.config/ksei-mcp
   cat > ~/.config/ksei-mcp/config.json << EOF
   {
     "credentials": {
       "username": "your-email@domain.com",
       "password": "your-password"
     },
     "auth_store_path": "~/.cache/ksei-mcp/auth"
   }
   EOF
   ```

## Usage

### MCP Client Integration

1. **Add MCP config**:
   
   Edit `mcp.json`:

   ```json
   {
     "mcpServers": {
       "ksei": {
         "command": "python",
         "args": ["/path/to/ksei-mcp/ksei_mcp.py"],
         "env": {
           "PYTHONPATH": "/path/to/ksei-mcp",
           "KSEI_USERNAME": "your-email@domain.com",
           "KSEI_PASSWORD": "your-password",
           "KSEI_AUTH_PATH": "~/.cache/ksei-mcp/auth"
         }
       }
     }
   }
   ```

2. **Use in conversations**:
   ```
   Show me my KSEI portfolio summary
   What are my current cash balances?
   List my equity holdings
   Get my account information
   ```

### Standalone Usage

```bash
python ksei_mcp.py
```

### Programmatic Usage

```python
from ksei_mcp import Client, FileAuthStore

# Initialize client
auth_store = FileAuthStore(directory="./auth_store")
client = Client(
    auth_store=auth_store,
    username="your-email@domain.com", 
    password="your-password"
)

# Get portfolio data
summary = client.get_portfolio_summary()
print(f"Total portfolio value: {summary.total}")

cash_balances = client.get_cash_balances()
for balance in cash_balances.data:
    print(f"Account {balance.account_number}: {balance.current_balance()}")
```

## Available Tools

### `configure_auth`
Configure KSEI authentication credentials (if not set via environment).

**Parameters:**
- `username` (string, required): KSEI username/email
- `password` (string, required): KSEI password  
- `auth_store_path` (string, optional): Path to store auth tokens

### `get_portfolio_summary`
Get portfolio summary with total value and asset breakdown.

**Returns:** Portfolio summary with total value and breakdown by asset type (equity, mutual fund, cash, bond, other).

### `get_cash_balances`
Get cash balances across all accounts.

**Returns:** List of cash balances with account details, currency, and current balance.

### `get_holdings`
Get holdings for specific asset type.

**Parameters:**
- `asset_type` (string, required): One of "equity", "mutual_fund", "bond", "other"

**Returns:** Holdings data with quantities, prices, and current values.

### `get_account_info`
Get account identity information.

**Returns:** Global identity data including investor ID, full name, contact details.

## Available Resources

### `ksei://portfolio/summary`
Portfolio summary with total value and asset breakdown.

### `ksei://portfolio/cash`
Cash balances across all accounts.

### `ksei://portfolio/equity`
Equity/stock holdings with current valuations.

### `ksei://portfolio/mutual-fund`
Mutual fund holdings.

### `ksei://portfolio/bond`
Bond holdings.

### `ksei://account/identity`
Global identity and account information.

## Configuration Options

### Environment Variables

- `KSEI_USERNAME`: KSEI account username/email
- `KSEI_PASSWORD`: KSEI account password
- `KSEI_AUTH_PATH`: Directory to store authentication tokens (default: `./auth_store`)

### Configuration File Locations

The server looks for configuration files in this order:
1. `~/.config/ksei-mcp/config.json`
2. `./config.json`

### Configuration File Format

```json
{
  "credentials": {
    "username": "your-email@domain.com",
    "password": "your-password"
  },
  "auth_store_path": "~/.cache/ksei-mcp/auth"
}
```

## Data Models

### PortfolioSummaryResponse
```json
{
  "total": 1500000.0,
  "details": [
    {
      "type": "EKUITAS",
      "amount": 1200000.0,
      "percent": 80.0
    }
  ]
}
```

### CashBalance
```json
{
  "id": 123,
  "account_number": "1234567890",
  "bank_id": "BCA",
  "currency": "IDR",
  "balance": 500000.0,
  "balance_idr": 500000.0,
  "status": 1
}
```

### ShareBalance
```json
{
  "account": "1234567890",
  "full_name": "BBCA - PT Bank Central Asia Tbk",
  "participant": "MANDIRI SEKURITAS",
  "balance_type": "AVAILABLE",
  "currency": "IDR",
  "amount": 1000.0,
  "closing_price": 9500.0
}
```

## Security Considerations

- **Credentials Storage**: Use environment variables or secure configuration files
- **Token Caching**: Authentication tokens are cached to minimize login requests
- **Token Expiration**: Automatic token refresh when expired
- **HTTPS**: All API communications use HTTPS
- **No Credential Logging**: Sensitive data is not logged

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   ```
   Error: Username and password are required
   ```
   - Ensure credentials are set via environment variables, .env file, or configuration file
   - Verify credentials are correct by logging into KSEI web interface

2. **Client Not Initialized**
   ```
   Error: KSEI client not initialized. Use configure_auth tool first.
   ```
   - Check credential configuration
   - Use `configure_auth` tool if auto-configuration failed

3. **Token Expired**
   ```
   Error: Token expired or invalid
   ```
   - Delete auth store directory to force re-authentication
   - Check if KSEI password was changed

4. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'ksei_client'
   ```
   - Ensure `ksei_client.py` is in the same directory as `ksei_mcp.py`
   - Check `PYTHONPATH` in Claude Desktop configuration

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export PYTHONPATH=/path/to/ksei-mcp
export KSEI_DEBUG=true
python ksei_mcp.py
```

## API Rate Limits

- KSEI API has undocumented rate limits
- The client implements automatic token refresh to minimize requests
- Cached authentication tokens are reused until expiration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Acknowledgements / Origin

This project is a Python adaptation of [**goksei**](https://github.com/chickenzord/goksei) by [@chickenzord](https://github.com/chickenzord), originally written in Go.

Credit to the original author for the core design and implementation ideas.

## License

This project is provided as-is for educational and personal use. Please ensure compliance with KSEI's terms of service.