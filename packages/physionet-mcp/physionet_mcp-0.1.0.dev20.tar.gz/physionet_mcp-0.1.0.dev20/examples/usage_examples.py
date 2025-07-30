"""
Usage Examples for PhysioNet MCP Server

This file shows example queries and usage patterns for the PhysioNet MCP server.
These examples would typically be run through Claude Desktop after configuring
the MCP server.
"""

# Example 1: Basic Database Querying
"""
Claude Query: "Show me the first 10 patients from MIMIC-IV"

Server Response using query_sql tool:
SELECT subject_id, gender, anchor_age 
FROM patients 
LIMIT 10
"""

# Example 2: Complex Analysis
"""
Claude Query: "Analyze ICU length of stay patterns in the AUMC database"

Server Response using run_analysis tool with admission_stats:
SELECT 
    CASE 
        WHEN los_hours < 24 THEN 'Short (< 1 day)'
        WHEN los_hours < 168 THEN 'Medium (1-7 days)'  
        ELSE 'Long (> 7 days)'
    END as stay_category,
    COUNT(*) as patient_count,
    AVG(los_hours) as avg_hours,
    MEDIAN(los_hours) as median_hours
FROM (
    SELECT 
        patientid,
        (dischargedtime - admittedtime) / 3600000 as los_hours
    FROM admissions 
    WHERE dischargedtime IS NOT NULL
)
GROUP BY stay_category
ORDER BY avg_hours
"""

# Example 3: Patient Timeline
"""
Claude Query: "Show me the complete timeline for patient 12345 in MIMIC-IV"

Server Response using get_patient_info and additional queries:
-- Patient demographics
SELECT p.subject_id, p.gender, p.anchor_age,
       a.hadm_id, a.admittime, a.dischtime
FROM patients p
JOIN admissions a ON p.subject_id = a.subject_id  
WHERE p.subject_id = '12345'

-- Vital signs during stay
SELECT charttime, itemid, value, valueuom
FROM chartevents 
WHERE subject_id = '12345' 
    AND itemid IN (220045, 220181, 220179)  -- HR, BP, Temp
ORDER BY charttime

-- Lab results
SELECT charttime, itemid, valuenum, valueuom
FROM labevents
WHERE subject_id = '12345'
ORDER BY charttime
"""

# Example 4: Cross-Database Comparison
"""
Claude Query: "Compare mortality rates between MIMIC-IV and eICU databases"

Server Response using multiple query_sql calls:

-- MIMIC-IV mortality
SELECT 
    'MIMIC-IV' as database,
    COUNT(*) as total_admissions,
    SUM(CASE WHEN hospital_expire_flag = 1 THEN 1 ELSE 0 END) as deaths,
    AVG(CASE WHEN hospital_expire_flag = 1 THEN 1.0 ELSE 0.0 END) * 100 as mortality_rate
FROM admissions

-- eICU mortality  
SELECT 
    'eICU' as database,
    COUNT(*) as total_admissions,
    SUM(CASE WHEN hospitaldischargestatus = 'Expired' THEN 1 ELSE 0 END) as deaths,
    AVG(CASE WHEN hospitaldischargestatus = 'Expired' THEN 1.0 ELSE 0.0 END) * 100 as mortality_rate  
FROM patient
"""

# Example 5: Waveform Database Analysis
"""
Claude Query: "Find all MIT-BIH records with atrial fibrillation annotations"

Server Response for WFDB database:
-- Note: This would require special handling for WFDB annotation files
SELECT 
    record_name,
    duration_minutes,
    sampling_frequency,
    annotation_count
FROM wfdb_records 
WHERE annotations LIKE '%AFIB%'
    OR annotations LIKE '%AF%'
ORDER BY record_name
"""

# Example 6: Database Schema Exploration
"""
Claude Query: "What tables are available in the AUMC database?"

Server Response using get_database_schema:
{
  "database": "aumc",
  "schema": {
    "tables": {
      "patients": {
        "columns": [
          {"name": "patientid", "type": "INTEGER"},
          {"name": "gender", "type": "VARCHAR"}, 
          {"name": "age", "type": "INTEGER"}
        ],
        "row_count": 23106
      },
      "admissions": {
        "columns": [
          {"name": "admissionid", "type": "INTEGER"},
          {"name": "patientid", "type": "INTEGER"},
          {"name": "admittedat", "type": "TIMESTAMP"}
        ],
        "row_count": 23106  
      }
    }
  }
}
"""

# Example 7: Time-Series Analysis
"""
Claude Query: "Show hourly vital sign trends for ICU patients"

Server Response:
SELECT 
    DATE_TRUNC('hour', charttime) as hour,
    AVG(CASE WHEN itemid = 220045 THEN valuenum END) as avg_heart_rate,
    AVG(CASE WHEN itemid = 220181 THEN valuenum END) as avg_sbp,
    AVG(CASE WHEN itemid = 220179 THEN valuenum END) as avg_temperature,
    COUNT(DISTINCT subject_id) as patient_count
FROM chartevents
WHERE itemid IN (220045, 220181, 220179)  -- HR, SBP, Temp
    AND valuenum IS NOT NULL
    AND charttime >= '2020-01-01'
GROUP BY DATE_TRUNC('hour', charttime)
ORDER BY hour
LIMIT 24
"""

# Example 8: Preparing a New Database
"""
Claude Query: "I want to analyze the PTB-XL ECG database. Can you prepare it for me?"

Server Response using prepare_database:
{
  "status": "preparation_started",
  "database": "ptb-xl", 
  "message": "Started preparation of ptb-xl. This may take some time.",
  "estimated_size_gb": 13.8,
  "steps": [
    "Downloading from https://physionet.org/files/ptb-xl/1.0.3/",
    "Converting CSV files to DuckDB format", 
    "Creating optimized indexes",
    "Database will be ready for querying"
  ]
}
"""

# Example 9: Advanced Filtering
"""  
Claude Query: "Find all female patients over 65 with cardiac conditions in MIMIC-IV"

Server Response:
SELECT DISTINCT
    p.subject_id,
    p.gender, 
    p.anchor_age,
    a.hadm_id,
    d.icd_code,
    d.short_title as diagnosis
FROM patients p
JOIN admissions a ON p.subject_id = a.subject_id
JOIN diagnoses_icd d ON a.hadm_id = d.hadm_id  
WHERE p.gender = 'F'
    AND p.anchor_age > 65
    AND (d.icd_code LIKE 'I%'      -- Cardiovascular diseases
         OR d.icd_code LIKE '410%'  -- Myocardial infarction  
         OR d.icd_code LIKE '428%') -- Heart failure
ORDER BY p.subject_id, a.admittime
LIMIT 100
"""

# Example 10: Data Quality Assessment
"""
Claude Query: "Check data quality and completeness for the AUMC database"

Server Response:
-- Table row counts
SELECT 
    'patients' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT patientid) as unique_patients
FROM patients
UNION ALL
SELECT 
    'vitals' as table_name, 
    COUNT(*) as total_rows,
    COUNT(DISTINCT patientid) as unique_patients  
FROM vitals

-- Missing value analysis
SELECT 
    'age' as column_name,
    COUNT(*) as total_records,
    COUNT(age) as non_null_records,
    COUNT(*) - COUNT(age) as missing_records,
    (COUNT(*) - COUNT(age)) * 100.0 / COUNT(*) as missing_percentage
FROM patients
UNION ALL  
SELECT
    'vital_values' as column_name,
    COUNT(*) as total_records, 
    COUNT(value) as non_null_records,
    COUNT(*) - COUNT(value) as missing_records,
    (COUNT(*) - COUNT(value)) * 100.0 / COUNT(*) as missing_percentage
FROM vitals
""" 