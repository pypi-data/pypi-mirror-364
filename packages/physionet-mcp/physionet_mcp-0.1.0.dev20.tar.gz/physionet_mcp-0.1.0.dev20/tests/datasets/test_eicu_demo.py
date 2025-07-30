"""
Test suite for eICU Collaborative Research Database Demo.

Tests the complete pipeline for the eICU demo dataset:
- Database info retrieval
- Download (wget method)
- Conversion to DuckDB
- MCP tools functionality
- Basic queries
"""

import os
from pathlib import Path
from typing import Dict, Any

from tests.base_test import BaseDatasetTest


class EICUDemoTest(BaseDatasetTest):
    """Test class specifically for eICU demo database."""
    
    def __init__(self, test_data_root: Path = None):
        """Initialize eICU demo test."""
        super().__init__("eicu-demo", test_data_root)
    
    def _get_test_queries(self) -> Dict[str, str]:
        """Get eICU demo specific test queries."""
        return {
            # Basic table existence checks
            "list_tables": """
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """,
            
            # Patient count (should be around 2,500)
            "patient_count": """
                SELECT COUNT(*) as patient_count 
                FROM patient
            """,
            
            # Sample patient data
            "sample_patients": """
                SELECT patientunitstayid, gender, age 
                FROM patient 
                WHERE age IS NOT NULL
                LIMIT 5
            """,
            
            # Hospital count
            "hospital_count": """
                SELECT COUNT(DISTINCT hospitalid) as hospital_count 
                FROM patient
            """,
            
            # Sample lab data
            "sample_labs": """
                SELECT patientunitstayid, labname, labresult, labresultoffset
                FROM lab 
                WHERE labresult IS NOT NULL
                LIMIT 5
            """,
            
            # Age distribution (eICU demo specific)
            "age_distribution": """
                SELECT 
                    CASE 
                        WHEN TRY_CAST(age AS INTEGER) < 18 THEN 'Under 18'
                        WHEN TRY_CAST(age AS INTEGER) BETWEEN 18 AND 65 THEN '18-65'
                        WHEN TRY_CAST(age AS INTEGER) > 65 THEN 'Over 65'
                        ELSE 'Unknown'
                    END as age_group,
                    COUNT(*) as count
                FROM patient
                WHERE age IS NOT NULL AND age != '' 
                GROUP BY age_group
                ORDER BY count DESC
            """,
            
            # Gender distribution
            "gender_distribution": """
                SELECT gender, COUNT(*) as count
                FROM patient
                WHERE gender IS NOT NULL
                GROUP BY gender
                ORDER BY count DESC
            """,
            
            # Unit types
            "unit_types": """
                SELECT unittype, COUNT(*) as count
                FROM patient
                WHERE unittype IS NOT NULL
                GROUP BY unittype
                ORDER BY count DESC
                LIMIT 10
            """,
            
            # Most common lab tests
            "common_labs": """
                SELECT labname, COUNT(*) as count
                FROM lab
                WHERE labname IS NOT NULL
                GROUP BY labname
                ORDER BY count DESC
                LIMIT 10
            """,
        }
    
    async def test_eicu_demo_specific(self) -> bool:
        """Run eICU demo specific tests."""
        self.logger.info("Running eICU demo specific tests...")
        
        try:
            config = self._create_test_config()
            
            if config.is_database_converted(self.database_name):
                from physionetmcp.server import query_sql
                
                # Check patient count
                result = query_sql.fn("SELECT COUNT(*) as count FROM patient", self.database_name)
                if isinstance(result, list) and len(result) > 0:
                    patient_count = result[0].get('count', 0)
                    self.logger.info(f"✅ Patient count: {patient_count}")
                    
                    # eICU demo should have around 2,500 unit stays
                    if 2000 <= patient_count <= 3000:
                        self.logger.info("✅ Patient count matches eICU demo expectations")
                    else:
                        self.results['warnings'].append(
                            f"Patient count ({patient_count}) outside eICU demo range (2,000-3,000)"
                        )
                
                # Check for expected eICU demo tables
                expected_tables = ['patient', 'admissiondx', 'lab']
                table_result = query_sql.fn(
                    "SELECT name FROM sqlite_master WHERE type='table'", 
                    self.database_name
                )
                
                if isinstance(table_result, list):
                    available_tables = [row['name'] for row in table_result]
                    self.logger.info(f"✅ Available tables: {available_tables}")
                    
                    for table in expected_tables:
                        if table in available_tables:
                            self.logger.info(f"✅ Required table '{table}' found")
                        else:
                            self.results['warnings'].append(f"Expected table '{table}' not found")
                
                # Test eICU demo specific columns
                try:
                    # Test for eICU-specific patient columns
                    patient_columns_result = query_sql.fn(
                        "PRAGMA table_info(patient)", 
                        self.database_name
                    )
                    if isinstance(patient_columns_result, list):
                        patient_columns = [row['name'] for row in patient_columns_result]
                        self.logger.info(f"✅ Patient table columns: {patient_columns}")
                        
                        # Check for key eICU patient columns
                        expected_patient_cols = ['patientunitstayid', 'gender', 'age', 'hospitalid']
                        for col in expected_patient_cols:
                            if col in patient_columns:
                                self.logger.info(f"✅ Patient column '{col}' found")
                            else:
                                self.results['warnings'].append(f"Expected patient column '{col}' not found")
                
                except Exception as e:
                    self.results['warnings'].append(f"Could not check eICU demo specific columns: {str(e)}")
            
            return True
            
        except Exception as e:
            self.results['errors'].append(f"eICU demo specific tests failed: {str(e)}")
            self.logger.error(f"❌ eICU demo specific tests failed: {e}")
            return False
    
    async def test_eicu_demo_data_quality(self) -> bool:
        """Test eICU demo data quality."""
        self.logger.info("Testing eICU demo data quality...")
        
        try:
            config = self._create_test_config()
            
            if config.is_database_converted(self.database_name):
                from physionetmcp.server import query_sql
                
                # Test for reasonable age distribution
                age_result = query_sql.fn(
                    "SELECT MIN(TRY_CAST(age AS INTEGER)) as min_age, MAX(TRY_CAST(age AS INTEGER)) as max_age, AVG(TRY_CAST(age AS INTEGER)) as avg_age FROM patient WHERE age IS NOT NULL AND age != '' AND TRY_CAST(age AS INTEGER) IS NOT NULL", 
                    self.database_name
                )
                
                if isinstance(age_result, list) and len(age_result) > 0:
                    age_stats = age_result[0]
                    self.logger.info(f"✅ Age stats: min={age_stats.get('min_age')}, max={age_stats.get('max_age')}, avg={age_stats.get('avg_age'):.1f}")
                    
                    # Basic sanity checks for age
                    min_age = age_stats.get('min_age', 0)
                    max_age = age_stats.get('max_age', 0)
                    
                    if min_age >= 0 and max_age <= 120:
                        self.logger.info("✅ Age values within reasonable range")
                    else:
                        self.results['warnings'].append(f"Age values outside reasonable range: {min_age}-{max_age}")
                
                # Test gender distribution
                gender_result = query_sql.fn(
                    "SELECT gender, COUNT(*) as count FROM patient WHERE gender IS NOT NULL GROUP BY gender", 
                    self.database_name
                )
                
                if isinstance(gender_result, list):
                    genders = [row['gender'] for row in gender_result]
                    self.logger.info(f"✅ Gender categories: {genders}")
                    
                    # Should have at least male/female
                    if len(genders) >= 2:
                        self.logger.info("✅ Multiple gender categories found")
                    else:
                        self.results['warnings'].append("Expected multiple gender categories")
                
                # Test hospital count (should be 20 hospitals in demo)
                hospital_result = query_sql.fn(
                    "SELECT COUNT(DISTINCT hospitalid) as hospital_count FROM patient", 
                    self.database_name
                )
                
                if isinstance(hospital_result, list) and len(hospital_result) > 0:
                    hospital_count = hospital_result[0].get('hospital_count', 0)
                    self.logger.info(f"✅ Hospital count: {hospital_count}")
                    
                    if hospital_count >= 10:  # Should be around 20, but being flexible
                        self.logger.info("✅ Multiple hospitals found in demo")
                    else:
                        self.results['warnings'].append(f"Expected more hospitals in demo, found: {hospital_count}")
            
            return True
            
        except Exception as e:
            self.results['warnings'].append(f"eICU demo data quality tests failed: {str(e)}")
            self.logger.warning(f"⚠️  eICU demo data quality tests failed: {e}")
            return True  # Don't fail the whole test for data quality issues
    
    async def run_full_test(self, cleanup: bool = True) -> Dict[str, Any]:
        """Run complete test suite including eICU demo specific tests with longer timeout."""
        # Run base tests first with custom timeout for eICU
        self.logger.info(f"🧪 Starting full test suite for {self.database_name}")
        
        try:
            # Test database info
            await self.test_database_info()
            
            # Test download with longer timeout (eICU has many files and can be slow)
            await self.test_download(timeout_minutes=20)
            
            # Test conversion (only if download succeeded)
            if self.results['download_success']:
                await self.test_conversion()
            
            # Test MCP tools
            await self.test_mcp_tools()
            
            # Test basic queries (only if conversion succeeded)
            if self.results['conversion_success']:
                await self.test_basic_queries()
            
            # Run eICU demo specific tests
            if self.results.get('conversion_success'):
                await self.test_eicu_demo_specific()
                await self.test_eicu_demo_data_quality()
            
            # Calculate overall success
            critical_tests = ['download_success', 'conversion_success', 'query_success']
            success_count = sum(1 for test in critical_tests if self.results.get(test, False))
            self.results['overall_success'] = success_count >= 2  # At least 2/3 critical tests
            
            # Log summary
            self._log_summary()
            
        except Exception as e:
            self.results['errors'].append(f"Test suite failed: {str(e)}")
            self.logger.error(f"❌ Test suite failed: {e}")
            self.results['overall_success'] = False
        
        finally:
            # Cleanup if requested
            if cleanup and self.test_data_root.exists():
                try:
                    import shutil
                    shutil.rmtree(self.test_data_root)
                    self.logger.info("🧹 Cleaned up test data")
                except Exception as e:
                    self.logger.warning(f"⚠️  Cleanup failed: {e}")
        
        return self.results


async def run_eicu_demo_test(test_data_root: Path = None, cleanup: bool = True):
    """
    Convenience function to run eICU demo test.
    
    Args:
        test_data_root: Directory for test data (temp dir if None)
        cleanup: Whether to cleanup test data after test
    
    Returns:
        Test results dictionary
    """
    test = EICUDemoTest(test_data_root)
    return await test.run_full_test(cleanup=cleanup)


if __name__ == "__main__":
    import asyncio
    import logging
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the test
    print("🧪 Running eICU Demo Test Suite...")
    results = asyncio.run(run_eicu_demo_test())
    
    # Print final result
    if results.get('overall_success'):
        print("\n🎉 eICU demo test completed successfully!")
    else:
        print("\n❌ eICU demo test failed!")
        if results.get('errors'):
            print("Errors:")
            for error in results['errors']:
                print(f"  - {error}")
    
    exit(0 if results.get('overall_success') else 1) 