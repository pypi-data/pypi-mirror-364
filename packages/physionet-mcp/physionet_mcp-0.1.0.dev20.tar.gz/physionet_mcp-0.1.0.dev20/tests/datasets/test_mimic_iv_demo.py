"""
Test suite for MIMIC-IV Demo database.

Tests the complete pipeline for the MIMIC-IV demo dataset:
- Database info retrieval
- Download (wget method)
- Conversion to DuckDB
- MCP tools functionality
- Basic queries
"""

import os
from pathlib import Path
from typing import Dict

from tests.base_test import BaseDatasetTest


class MimicIVDemoTest(BaseDatasetTest):
    """Test class specifically for MIMIC-IV Demo database."""
    
    def __init__(self, test_data_root: Path = None):
        """Initialize MIMIC-IV Demo test."""
        super().__init__("mimic-iv-demo", test_data_root)
    
    def _get_test_queries(self) -> Dict[str, str]:
        """Get MIMIC-IV Demo specific test queries."""
        return {
            # Basic table existence checks
            "list_tables": """
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """,
            
            # Patient count (should be around 100)
            "patient_count": """
                SELECT COUNT(*) as patient_count 
                FROM patients
            """,
            
            # Sample patient data
            "sample_patients": """
                SELECT subject_id, gender, anchor_age 
                FROM patients 
                LIMIT 5
            """,
            
            # Admission count
            "admission_count": """
                SELECT COUNT(*) as admission_count 
                FROM admissions
            """,
            
            # Sample admissions
            "sample_admissions": """
                SELECT hadm_id, subject_id, admittime, admission_type 
                FROM admissions 
                LIMIT 5
            """,
            
            # Lab events count (available in demo)
            "lab_events_count": """
                SELECT COUNT(*) as lab_events_count 
                FROM labevents
            """,
            
            # Join test - patients with admissions
            "patients_with_admissions": """
                SELECT p.subject_id, p.gender, COUNT(a.hadm_id) as admission_count
                FROM patients p
                LEFT JOIN admissions a ON p.subject_id = a.subject_id
                GROUP BY p.subject_id, p.gender
                LIMIT 5
            """,
            
            # Sample lab results (if exists)
            "sample_lab_results": """
                SELECT itemid, COUNT(*) as count
                FROM labevents
                GROUP BY itemid
                ORDER BY count DESC
                LIMIT 5
            """,
        }
    
    async def test_mimic_iv_demo_specific(self) -> bool:
        """Run MIMIC-IV Demo specific tests."""
        self.logger.info("Running MIMIC-IV Demo specific tests...")
        
        try:
            # Test that this is indeed the demo version (should have ~100 patients)
            config = self._create_test_config()
            
            if config.is_database_converted(self.database_name):
                from physionetmcp.server import query_sql
                
                # Check patient count
                result = query_sql.fn("SELECT COUNT(*) as count FROM patients", self.database_name)
                if isinstance(result, list) and len(result) > 0:
                    patient_count = result[0].get('count', 0)
                    self.logger.info(f"✅ Patient count: {patient_count}")
                    
                    # Demo should have around 100 patients
                    if 50 <= patient_count <= 150:
                        self.logger.info("✅ Patient count matches demo expectations")
                    else:
                        self.results['warnings'].append(
                            f"Patient count ({patient_count}) outside demo range (50-150)"
                        )
                
                # Check for expected tables
                expected_tables = ['patients', 'admissions', 'labevents']
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
            
            return True
            
        except Exception as e:
            self.results['errors'].append(f"MIMIC-IV Demo specific tests failed: {str(e)}")
            self.logger.error(f"❌ MIMIC-IV Demo specific tests failed: {e}")
            return False
    
    async def run_full_test(self, cleanup: bool = True) -> Dict[str, any]:
        """Run complete test suite including MIMIC-IV Demo specific tests."""
        # Run base tests first
        results = await super().run_full_test(cleanup=False)
        
        # Run MIMIC-IV Demo specific tests
        if results.get('conversion_success'):
            await self.test_mimic_iv_demo_specific()
        
        # Cleanup if requested
        if cleanup and self.test_data_root.exists():
            try:
                import shutil
                shutil.rmtree(self.test_data_root)
                self.logger.info("🧹 Cleaned up test data")
            except Exception as e:
                self.logger.warning(f"⚠️  Cleanup failed: {e}")
        
        return self.results


async def run_mimic_iv_demo_test(test_data_root: Path = None, cleanup: bool = True):
    """
    Convenience function to run MIMIC-IV Demo test.
    
    Args:
        test_data_root: Directory for test data (temp dir if None)
        cleanup: Whether to cleanup test data after test
    
    Returns:
        Test results dictionary
    """
    test = MimicIVDemoTest(test_data_root)
    return await test.run_full_test(cleanup=cleanup)


if __name__ == "__main__":
    import asyncio
    import logging
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the test
    print("🧪 Running MIMIC-IV Demo Test Suite...")
    results = asyncio.run(run_mimic_iv_demo_test())
    
    # Print final result
    if results.get('overall_success'):
        print("\n🎉 MIMIC-IV Demo test completed successfully!")
    else:
        print("\n❌ MIMIC-IV Demo test failed!")
        if results.get('errors'):
            print("Errors:")
            for error in results['errors']:
                print(f"  - {error}")
    
    exit(0 if results.get('overall_success') else 1) 