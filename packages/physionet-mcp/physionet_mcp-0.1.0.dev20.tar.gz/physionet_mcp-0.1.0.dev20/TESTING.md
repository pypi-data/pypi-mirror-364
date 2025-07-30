# Testing PhysioNet MCP Server

This guide walks you through testing the PhysioNet MCP server with Claude Desktop, covering both open-access and credentialed databases.

## 🔄 **Development vs Production Testing**

- **🛠️ Development**: Use `"command": "python"` with absolute paths to your local project
- **📦 Production**: Use `"command": "uv"` with `--with physionetmcp` (requires PyPI publishing)

Choose the configuration method that matches your current setup!

## 🚀 Quick Start Testing

### Step 1: Basic Configuration Test

**Production Configuration (after PyPI publishing):**
```json
{
  "mcpServers": {
    "physionetmcp-test": {
      "command": "uv",
      "args": ["run", "--with", "physionetmcp", "physionetmcp", "run"],
      "db": ["aumc"],
      "dataRoot": "~/physionet_test"
    }
  }
}
```

**Development Configuration (before PyPI publishing):**
```json
{
  "mcpServers": {
    "physionetmcp-dev": {
      "command": "python",
      "args": ["/full/path/to/your/physionetmcp/cli.py", "run"],
      "db": ["aumc"],
      "dataRoot": "~/physionet_test"
    }
  }
}
```

**Alternative Development Setup:**  
```json
{
  "mcpServers": {
    "physionetmcp-dev": {
      "command": "python",
      "args": ["-m", "physionetmcp.cli", "run"],
      "cwd": "/path/to/your/physionetmcp/project",
      "db": ["aumc"],
      "dataRoot": "~/physionet_test"
    }
  }
}
```

### Step 2: Restart Claude Desktop

Completely restart Claude Desktop after updating the configuration.

### Step 3: Verify MCP Connection

Look for the 🔨 (hammer) icon in Claude's input box. If missing:
1. Check the configuration file syntax
2. Review logs: `tail -f ~/Library/Logs/Claude/mcp*.log`
3. Ensure the path to the config file is correct

## 📋 Test Scenarios

### Test 1: List Available Databases

**Query**: "What PhysioNet databases are available?"

**Expected Response**: JSON showing configured databases with their status:
```json
{
  "total_databases": 1,
  "storage_format": "duckdb", 
  "databases": {
    "aumc": {
      "title": "Amsterdam University Medical Centers Database",
      "downloaded": false,
      "converted": false,
      "size_gb": 12.5
    }
  }
}
```

### Test 2: Database Schema Exploration

**Query**: "Show me the schema for the AUMC database"

**Expected Behavior**:
- If not downloaded: Error message about database not being ready
- If downloaded: Schema information with tables and columns

### Test 3: Simple Query Test

**Query**: "Run this SQL on AUMC: SELECT COUNT(*) as total_patients FROM patients"

**Expected Behavior**:
- Database will be automatically prepared if not ready
- Query results returned as JSON

### Test 4: Database Preparation

**Query**: "Please prepare the AUMC database for querying"

**Expected Response**:
```json
{
  "status": "preparation_started",
  "database": "aumc",
  "message": "Started preparation of aumc. This may take some time.",
  "estimated_size_gb": 12.5
}
```

## 🔐 Testing with Credentials

### Test 5: MIMIC-IV Setup

**Configuration**:
```json
{
  "mcpServers": {
    "physionetmcp": {
      "command": "uv",
      "args": ["run", "--with", "physionetmcp", "physionetmcp", "run"],
      "db": ["mimic-iv", "aumc"],
      "dataRoot": "~/physionet_data",
      "env": {
        "PHYSIONET_USERNAME": "your_username",
        "PHYSIONET_PASSWORD": "your_password"
      }
    }
  }
}
```

**Query**: "List patients from MIMIC-IV: SELECT subject_id, gender, anchor_age FROM patients LIMIT 10"

## 🛠️ Advanced Testing

### Test 6: Multiple Databases

**Configuration**:
```json
{
  "db": ["aumc", "mitdb", "ptb-xl"],
  "storageFormat": "duckdb"
}
```

**Query**: "Compare the number of records between AUMC and MIT-BIH databases"

### Test 7: Custom Analysis

**Query**: "Run the 'patient_summary' analysis on the AUMC database"

**Expected**: Demographics overview with patient counts and statistics

### Test 8: Error Handling

**Query**: "Query a non-existent database: SELECT * FROM fake_database"

**Expected**: Clear error message about database not being configured

## 🐛 Troubleshooting Tests

### Connection Issues

**Symptoms**: No 🔨 icon, "Server not responding" errors

**Check**:
1. Configuration file syntax (use JSON validator)
2. MCP logs: `tail -f ~/Library/Logs/Claude/mcp*.log`
3. uv installation: `uv --version`

**Common Issues**:
```bash
# Wrong file location
~/Library/Application Support/Claude/claude_desktop_config.json

# JSON syntax error
# Use jsonlint or similar to validate

# Permission issues
chmod 644 ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Download Issues

**Symptoms**: "Database not found", "Download failed" errors

**Check**:
1. Internet connection
2. Disk space in `dataRoot` directory
3. PhysioNet credentials (for credentialed databases)

**Debug Steps**:
```bash
# Check available space
df -h ~/physionet_data

# Test credentials manually
curl -u "username:password" https://physionet.org/files/mimiciv/

# Check logs for specific error messages
grep -i error ~/Library/Logs/Claude/mcp*.log
```

### Performance Testing

**Test Large Database**:
```json
{
  "db": ["mimic-iv"],
  "maxResultRows": 1000,
  "queryTimeoutSeconds": 300
}
```

**Query**: "SELECT admission_type, COUNT(*) FROM admissions GROUP BY admission_type"

**Monitor**:
- Response time
- Memory usage
- Database file sizes in `dataRoot`

## ✅ Test Checklist

Before considering the setup complete, verify:

- [ ] MCP connection works (🔨 icon visible)
- [ ] Can list available databases
- [ ] Open database downloads and converts successfully
- [ ] Can query converted database
- [ ] Error messages are clear and helpful
- [ ] Credentials work for protected databases (if applicable)
- [ ] Performance is acceptable for your use case

## 🔍 Log Analysis

### Key Log Messages

**Successful Connection**:
```
[INFO] PhysioNet MCP Server initialized successfully
[INFO] Loaded configuration for 3 databases
```

**Download Progress**:
```
[INFO] Downloading database aumc to /path/to/data
[INFO] Successfully downloaded aumc
```

**Query Execution**:
```
[DEBUG] Executing query on aumc: SELECT COUNT(*) FROM patients
[INFO] Query completed in 0.5s
```

**Error Patterns**:
```
[ERROR] Database file not found: /path/to/aumc.duckdb
[ERROR] Failed to download aumc: Authentication failed
[WARNING] Query timeout exceeded: 300s
```

## 📊 Performance Benchmarks

### Expected Performance

| Database | Download Time | Conversion Time | Query Response |
|----------|--------------|-----------------|----------------|
| AUMC     | 10-30 min    | 5-15 min       | < 1s           |
| MIT-BIH  | 1-2 min      | < 1 min        | < 0.1s         |
| PTB-XL   | 5-15 min     | 2-5 min        | < 1s           |
| MIMIC-IV | 2-6 hours    | 30-60 min      | 1-5s           |

*Times vary based on internet speed, disk I/O, and system specs*

## 🚨 Known Issues

### Common Problems

1. **Node.js Version**: Claude uses system Node.js. Ensure version 18+
2. **Path Spaces**: Avoid spaces in `dataRoot` paths on Windows
3. **Network Timeouts**: Large databases may timeout on slow connections
4. **Memory Usage**: MIMIC-IV conversion requires 8GB+ RAM

### Workarounds

```json
{
  "maxConcurrentDownloads": 1,
  "queryTimeoutSeconds": 600,
  "dataRoot": "/Users/name/data"
}
```

## 📞 Getting Help

If tests fail:

1. **Check logs** first - most issues show clear error messages
2. **Verify configuration** with a JSON validator
3. **Test with open databases** before trying credentialed ones
4. **Check system requirements** (disk space, memory, network)
5. **Report issues** with log snippets and configuration details

Remember: Start simple with open databases, then gradually add complexity! 