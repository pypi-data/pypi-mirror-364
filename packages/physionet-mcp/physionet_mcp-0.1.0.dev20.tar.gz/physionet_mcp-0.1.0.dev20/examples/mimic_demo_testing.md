# Testing with MIMIC Demo Data

This guide shows how to test the PhysioNet MCP server using MIMIC demo datasets, which are small sample datasets perfect for testing without waiting for large downloads.

## 🎯 Why Use Demo Data?

- **Fast**: Download in minutes instead of hours
- **Small**: ~50MB vs 45GB for full MIMIC-IV
- **Complete**: Contains all the same tables and structure
- **No Credentials**: Open access, no PhysioNet account needed
- **Perfect for Testing**: Verify your setup works before committing to large downloads

## 📋 Quick Setup

### Configuration for Demo Testing

```json
{
  "mcpServers": {
    "physionet-demo": {
      "command": "uv",
      "args": ["run", "--with", "physionetmcp", "physionetmcp", "run"],
      
      "db": ["mimic-iv-demo", "aumc"], 
      "dataRoot": "~/physionet_demo_data",
      "storageFormat": "duckdb",
      "maxResultRows": 100
    }
  }
}
```

### Sample Queries for Demo Data

**1. Basic Data Exploration**
```
List available databases and show me the schema for MIMIC-IV demo
```

**2. Patient Demographics**
```sql
SELECT 
  gender,
  COUNT(*) as patient_count,
  AVG(anchor_age) as avg_age,
  MIN(anchor_age) as min_age, 
  MAX(anchor_age) as max_age
FROM patients 
GROUP BY gender
```

**3. Admission Analysis**
```sql
SELECT 
  admission_type,
  COUNT(*) as admissions,
  AVG(los) as avg_length_of_stay
FROM admissions 
GROUP BY admission_type
ORDER BY admissions DESC
```

**4. ICU Stays Overview**
```sql
SELECT 
  first_careunit,
  COUNT(*) as icu_stays,
  AVG(los) as avg_los_days
FROM icustays 
GROUP BY first_careunit
ORDER BY icu_stays DESC
```

**5. Cross-Database Comparison**
```
Compare the patient demographics between MIMIC demo and AUMC databases
```

## 🔍 What's In the Demo Data?

### MIMIC-IV Demo Structure
- **~100 patients** (vs 315K in full dataset)
- **All core tables**: patients, admissions, icustays, chartevents, labevents
- **Same schema**: Identical structure to full MIMIC-IV
- **Real relationships**: Proper foreign keys and data integrity
- **Time span**: Subset covering typical ICU scenarios

### Sample Counts (Approximate)
```sql
SELECT 'patients' as table_name, COUNT(*) as rows FROM patients
UNION ALL
SELECT 'admissions', COUNT(*) FROM admissions  
UNION ALL
SELECT 'icustays', COUNT(*) FROM icustays
UNION ALL  
SELECT 'chartevents', COUNT(*) FROM chartevents
UNION ALL
SELECT 'labevents', COUNT(*) FROM labevents
```

Expected results:
- patients: ~100
- admissions: ~120  
- icustays: ~140
- chartevents: ~15,000
- labevents: ~8,000

## 🚀 Advanced Demo Queries

### Patient Timeline Analysis
```sql
-- Get complete timeline for a patient
WITH patient_events AS (
  SELECT 
    p.subject_id,
    a.hadm_id,
    a.admittime,
    a.dischtime,
    i.intime as icu_intime,
    i.outtime as icu_outtime,
    i.first_careunit
  FROM patients p
  JOIN admissions a ON p.subject_id = a.subject_id
  LEFT JOIN icustays i ON a.hadm_id = i.hadm_id
  WHERE p.subject_id = 10000032  -- Replace with actual subject_id
)
SELECT * FROM patient_events
ORDER BY admittime
```

### Vital Signs Trends
```sql
-- Heart rate trends for ICU patients
SELECT 
  DATE(charttime) as date,
  AVG(valuenum) as avg_heart_rate,
  COUNT(*) as measurements
FROM chartevents 
WHERE itemid = 220045  -- Heart rate
  AND valuenum BETWEEN 0 AND 300  -- Filter outliers
GROUP BY DATE(charttime)
ORDER BY date
```

### Lab Values Analysis
```sql
-- Most common lab tests
SELECT 
  d.label,
  COUNT(*) as test_count,
  AVG(l.valuenum) as avg_value
FROM labevents l
JOIN d_labitems d ON l.itemid = d.itemid
WHERE l.valuenum IS NOT NULL
GROUP BY d.label
ORDER BY test_count DESC
LIMIT 10
```

## 🎮 Interactive Testing Session

### Step 1: Basic Verification
```
"What databases are available and what's their status?"
```

### Step 2: Schema Exploration  
```
"Show me the complete schema for the MIMIC-IV demo database with table sizes"
```

### Step 3: Sample Analysis
```
"Run a comprehensive patient demographics analysis on the MIMIC demo data"
```

### Step 4: Comparison Query
```
"Compare the average length of stay between different ICU types in the demo data"
```

### Step 5: Advanced Analytics
```
"Find patients with the longest ICU stays and show their admission details"
```

## 📊 Expected Performance

With demo data, you should see:

| Operation | Time | Notes |
|-----------|------|-------|
| Download | 2-5 minutes | Much faster than full datasets |
| Conversion | 30-60 seconds | Small data converts quickly |
| Simple queries | <100ms | Very responsive |
| Complex queries | <1 second | Even joins are fast |

## 🔧 Troubleshooting Demo Setup

### Common Issues

**1. Demo data not found**
```
Error: Database 'mimic-iv-demo' not configured
```
*Solution*: Ensure the demo dataset is in the database registry

**2. Still downloading full dataset**
```
Started preparation of mimic-iv. This may take some time.
estimated_size_gb: 45.0
```
*Solution*: Check you're using `mimic-iv-demo`, not `mimic-iv`

**3. Empty results**
```
Query returned no results
```
*Solution*: Demo data has limited patients - use broader queries

### Verification Commands

```bash
# Check download location
ls -la ~/physionet_demo_data/

# Verify demo database size (should be ~50MB, not GBs)
du -sh ~/physionet_demo_data/mimic-iv-demo/

# Check converted database
ls -la ~/physionet_demo_data/mimic-iv-demo/*.duckdb
```

## 🎯 Demo vs Production

| Aspect | Demo Data | Production Data |
|--------|-----------|-----------------|
| Size | ~50MB | 45GB (MIMIC-IV) |
| Patients | ~100 | 315K+ |
| Download | 2-5 min | 2-6 hours |
| Use Case | Testing, learning | Research, analysis |
| Credentials | None needed | PhysioNet account |

## 💡 Pro Tips

1. **Start with demo**: Always test your setup with demo data first
2. **Use small limits**: Add `LIMIT 10` to queries while testing
3. **Check schemas**: Verify table structures match expectations  
4. **Test tools**: Try all MCP tools with demo data before production
5. **Performance baseline**: Demo performance predicts production behavior

## 🚀 Next Steps

Once demo testing works perfectly:

1. **Add credentials** for protected datasets
2. **Scale up** to full databases gradually  
3. **Optimize queries** based on demo performance
4. **Set up monitoring** for production downloads
5. **Document workflows** that worked with demo data

The demo data gives you everything you need to verify your PhysioNet MCP setup works correctly before committing to multi-gigabyte downloads! 