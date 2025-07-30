# PhysioNet MCP Server Testing Guide

Comprehensive testing framework for validating PhysioNet datasets, server functionality, and MCP protocol compliance.

## 🏗️ **Test Structure**

```
tests/
├── __init__.py                     # Test package initialization
├── base_test.py                    # Base test class for datasets
├── run_dataset_tests.py            # Main test runner (executable)
├── datasets/                       # Dataset-specific tests
│   ├── test_mimic_iv_demo.py       # MIMIC-IV Demo tests
│   └── test_aumc.py                # AUMC tests
├── integration/                    # Integration tests
│   └── test_mcp_server.py          # MCP server integration tests
└── unit/                           # Unit tests (future)
```

## 🚀 **Quick Start**

### **Prerequisites**
```bash
# Set credentials (for credentialed databases)
export PHYSIONET_USERNAME="your_username"
export PHYSIONET_PASSWORD="your_password"

# Ensure dependencies are installed
uv sync --dev
```

### **Run All Tests**
```bash
# Run all dataset tests
python tests/run_dataset_tests.py

# Or make it executable and run directly
chmod +x tests/run_dataset_tests.py
./tests/run_dataset_tests.py
```

### **Run Specific Dataset Tests**
```bash
# Test only MIMIC-IV Demo
python tests/run_dataset_tests.py --datasets mimic-iv-demo

# Test only AUMC
python tests/run_dataset_tests.py --datasets aumc

# Test both
python tests/run_dataset_tests.py --datasets mimic-iv-demo aumc
```

### **Run Integration Tests**
```bash
# Test MCP server functionality
python tests/integration/test_mcp_server.py
```

## 📊 **Test Categories**

### **1. Dataset Tests**
Complete pipeline testing for each PhysioNet database:

- ✅ **Database Info**: Registry lookup and metadata validation
- ✅ **Download**: Data retrieval from PhysioNet (wget/S3/WFDB)
- ✅ **Conversion**: Transform to efficient storage (DuckDB/Parquet)
- ✅ **MCP Tools**: Server functionality and tool registration
- ✅ **Queries**: SQL query execution and data validation

### **2. Integration Tests**
End-to-end MCP server functionality:

- ✅ **Server Initialization**: FastMCP server startup
- ✅ **Configuration Loading**: Settings validation
- ✅ **Tool Registration**: MCP protocol compliance
- ✅ **Protocol Testing**: JSON-RPC 2.0 message handling

### **3. Unit Tests** (Future)
Individual component testing:

- Configuration validation
- Database registry operations
- Download manager functionality
- Storage converter operations

## 🧪 **Running Tests**

### **Basic Usage**
```bash
# Run all tests with default settings
python tests/run_dataset_tests.py

# Run with verbose output
python tests/run_dataset_tests.py --verbose

# Keep test data for inspection
python tests/run_dataset_tests.py --no-cleanup
```

### **Advanced Options**
```bash
# Specify custom test data directory
python tests/run_dataset_tests.py --test-data-root /tmp/physionet_tests

# Save results to custom file
python tests/run_dataset_tests.py --output-file my_test_results.json

# Combine options
python tests/run_dataset_tests.py \
    --datasets mimic-iv-demo \
    --test-data-root /tmp/test \
    --no-cleanup \
    --verbose \
    --output-file demo_test.json
```

## 📋 **Test Results**

### **Console Output**
Tests provide real-time progress updates:
```
🧪 Starting full test suite for mimic-iv-demo
[MIMIC-IV-DEMO] INFO: Testing database info retrieval...
[MIMIC-IV-DEMO] INFO: ✅ Database info: MIMIC-IV Clinical Database Demo (AccessType.OPEN)
[MIMIC-IV-DEMO] INFO: Testing database download...
[MIMIC-IV-DEMO] INFO: ✅ Download completed in 15.2s
[MIMIC-IV-DEMO] INFO: Testing database conversion...
[MIMIC-IV-DEMO] INFO: ✅ Conversion completed in 3.4s
[MIMIC-IV-DEMO] INFO: ✅ Tables: ['patients', 'admissions', 'icustays']
```

### **JSON Results**
Detailed results saved to `dataset_test_results.json`:
```json
{
  "timestamp": 1703123456.789,
  "summary": {
    "total_tests": 2,
    "passed_tests": 2,
    "failed_tests": 0,
    "success_rate": 100.0,
    "total_errors": 0,
    "total_warnings": 1,
    "total_time": 45.6
  },
  "results": {
    "mimic-iv-demo": {
      "overall_success": true,
      "download_success": true,
      "download_time": 15.2,
      "conversion_success": true,
      "conversion_time": 3.4,
      "query_success": true,
      "database_info": {
        "name": "mimic-iv-demo",
        "title": "MIMIC-IV Clinical Database Demo",
        "access_type": "AccessType.OPEN",
        "size_gb": 0.1,
        "patient_count": 100
      },
      "errors": [],
      "warnings": ["Schema not available - database not yet downloaded"]
    }
  }
}
```

## 🎯 **Test Scenarios**

### **MIMIC-IV Demo Database**
- **Size**: ~100MB (100 patients)
- **Access**: Open (no credentials required)
- **Tests**: 
  - Patient count validation (~100 patients)
  - Table structure verification
  - Basic SQL queries
  - Data quality checks

### **AUMC Database**
- **Size**: ~12.5GB (23,106 patients) 
- **Access**: Open (no credentials required)
- **Tests**:
  - Patient count validation (~23K patients)
  - Age distribution analysis
  - Gender distribution validation
  - Data quality assessment

## 🔧 **Customizing Tests**

### **Adding New Dataset Tests**
1. Create new test class inheriting from `BaseDatasetTest`:
```python
from tests.base_test import BaseDatasetTest

class MyDatabaseTest(BaseDatasetTest):
    def __init__(self, test_data_root=None):
        super().__init__("my-database", test_data_root)
    
    def _get_test_queries(self):
        return {
            "patient_count": "SELECT COUNT(*) FROM patients",
            # Add database-specific queries
        }
```

2. Add to test runner in `tests/run_dataset_tests.py`

### **Custom Queries**
Override `_get_test_queries()` method for database-specific validation:
```python
def _get_test_queries(self):
    return {
        "basic_count": "SELECT COUNT(*) as total FROM main_table",
        "data_quality": "SELECT AVG(age) as avg_age FROM patients WHERE age > 0",
        "table_structure": "SELECT name FROM sqlite_master WHERE type='table'"
    }
```

## 🚨 **Troubleshooting**

### **Common Issues**

**1. Download Failures**
```bash
# Check network connectivity
curl -I https://physionet.org

# Verify credentials (if needed)
echo $PHYSIONET_USERNAME
echo $PHYSIONET_PASSWORD
```

**2. Conversion Errors**  
```bash
# Check disk space
df -h

# Verify raw data integrity
ls -la /path/to/test/data/database_name/
```

**3. Query Failures**
```bash
# Check database file exists
ls -la /path/to/test/data/database_name.duckdb

# Test DuckDB connection manually
python -c "import duckdb; conn = duckdb.connect('test.duckdb'); print(conn.execute('SELECT 1').fetchall())"
```

### **Debug Mode**
```bash
# Enable verbose logging
python tests/run_dataset_tests.py --verbose

# Keep test data for manual inspection
python tests/run_dataset_tests.py --no-cleanup --test-data-root /tmp/debug_test

# Test individual components
python tests/datasets/test_mimic_iv_demo.py
```

### **Environment Issues**
```bash
# Check Python version (requires 3.10+)
python --version

# Verify dependencies
uv sync --dev

# Check imports
python -c "from physionetmcp.server import initialize_server; print('✅ Imports OK')"
```

## 📈 **Performance Benchmarks**

### **Expected Test Times**

| Database      | Download | Conversion | Total  | Size   |
|---------------|----------|------------|--------|--------|
| mimic-iv-demo | ~15-30s  | ~3-10s     | ~45s   | 100MB  |
| aumc          | ~5-15min | ~30-60s    | ~20min | 12.5GB |

### **System Requirements**
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 50GB free space for full tests
- **Network**: Stable internet connection

## 🎯 **Continuous Integration**

### **GitHub Actions Example**
```yaml
name: Dataset Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --dev
      
      - name: Run integration tests
        run: python tests/integration/test_mcp_server.py
      
      - name: Run dataset tests (demo only)
        run: python tests/run_dataset_tests.py --datasets mimic-iv-demo
        env:
          PHYSIONET_USERNAME: ${{ secrets.PHYSIONET_USERNAME }}
          PHYSIONET_PASSWORD: ${{ secrets.PHYSIONET_PASSWORD }}
```

## 📚 **Best Practices**

1. **Run integration tests first** to verify basic functionality
2. **Start with small datasets** (mimic-iv-demo) before larger ones
3. **Set credentials** as environment variables, never hardcode
4. **Use `--no-cleanup`** for debugging failed tests
5. **Monitor disk space** when testing large datasets
6. **Save test results** for performance tracking over time

## 🎉 **Success Criteria**

A successful test run should show:
- ✅ All critical tests passing (download, conversion, MCP tools)
- ⚠️  Warnings acceptable (e.g., "schema not available before download")
- ❌ Zero critical errors
- 📊 Performance within expected ranges
- 🎯 Overall success rate > 90% 