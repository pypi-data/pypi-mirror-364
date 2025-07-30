#!/usr/bin/env python3
"""
Comprehensive test runner for PhysioNet MCP Server datasets.

Runs tests for multiple datasets and provides detailed reporting.
"""

import asyncio
import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.datasets.test_mimic_iv_demo import run_mimic_iv_demo_test
from tests.datasets.test_eicu_demo import run_eicu_demo_test


class DatasetTestRunner:
    """Comprehensive test runner for PhysioNet datasets."""
    
    def __init__(self, test_data_root: Path = None, cleanup: bool = True):
        """
        Initialize test runner.
        
        Args:
            test_data_root: Root directory for test data (uses temp if None)
            cleanup: Whether to cleanup test data after tests
        """
        self.test_data_root = test_data_root
        self.cleanup = cleanup
        self.results = {}
        self.start_time = None
        self.end_time = None
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('dataset_tests.log')
            ]
        )
        self.logger = logging.getLogger('DatasetTestRunner')
    
    async def run_mimic_iv_demo_test(self) -> Dict[str, Any]:
        """Run MIMIC-IV Demo test."""
        self.logger.info("🧪 Running MIMIC-IV Demo test...")
        
        try:
            test_root = self.test_data_root / "mimic-iv-demo" if self.test_data_root else None
            return await run_mimic_iv_demo_test(test_root, self.cleanup)
        except Exception as e:
            self.logger.error(f"❌ MIMIC-IV Demo test failed with exception: {e}")
            return {
                'overall_success': False,
                'errors': [f"Test runner exception: {str(e)}"],
                'warnings': [],
                'database_info': None
            }
    
    async def run_eicu_demo_test(self) -> Dict[str, Any]:
        """Run eICU demo test."""
        self.logger.info("🧪 Running eICU demo test...")
        
        try:
            test_root = self.test_data_root / "eicu-demo" if self.test_data_root else None
            return await run_eicu_demo_test(test_root, self.cleanup)
        except Exception as e:
            self.logger.error(f"❌ eICU demo test failed with exception: {e}")
            return {
                'overall_success': False,
                'errors': [f"Test runner exception: {str(e)}"],
                'warnings': [],
                'database_info': None
            }
    
    async def run_all_tests(self, datasets: List[str] = None) -> Dict[str, Any]:
        """
        Run tests for all specified datasets.
        
        Args:
            datasets: List of dataset names to test (defaults to all supported)
        
        Returns:
            Complete test results
        """
        if datasets is None:
            datasets = ['mimic-iv-demo', 'eicu-demo']
        
        self.start_time = time.time()
        self.logger.info(f"🚀 Starting dataset tests for: {', '.join(datasets)}")
        
        # Available test functions
        test_functions = {
            'mimic-iv-demo': self.run_mimic_iv_demo_test,
            'eicu-demo': self.run_eicu_demo_test
        }
        
        # Run tests
        for dataset in datasets:
            if dataset not in test_functions:
                self.logger.warning(f"⚠️  Unknown dataset: {dataset}")
                self.results[dataset] = {
                    'overall_success': False,
                    'errors': [f'Unknown dataset: {dataset}'],
                    'warnings': [],
                    'database_info': None
                }
                continue
            
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Testing dataset: {dataset.upper()}")
            self.logger.info('='*60)
            
            # Run the test
            test_result = await test_functions[dataset]()
            self.results[dataset] = test_result
            
            # Log immediate result
            if test_result.get('overall_success'):
                self.logger.info(f"✅ {dataset} test PASSED")
            else:
                self.logger.error(f"❌ {dataset} test FAILED")
        
        self.end_time = time.time()
        
        # Generate summary
        self._generate_summary()
        
        return {
            'results': self.results,
            'summary': self._get_summary_stats(),
            'total_time': self.end_time - self.start_time
        }
    
    def _get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for all tests."""
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result.get('overall_success'))
        failed_tests = total_tests - passed_tests
        
        total_errors = sum(len(result.get('errors', [])) for result in self.results.values())
        total_warnings = sum(len(result.get('warnings', [])) for result in self.results.values())
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests, 
            'failed_tests': failed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'total_time': self.end_time - self.start_time if self.end_time and self.start_time else 0
        }
    
    def _generate_summary(self):
        """Generate and log test summary."""
        summary = self._get_summary_stats()
        
        self.logger.info("\n" + "="*80)
        self.logger.info("DATASET TEST SUMMARY")
        self.logger.info("="*80)
        
        self.logger.info(f"Total Tests: {summary['total_tests']}")
        self.logger.info(f"Passed: {summary['passed_tests']} ✅")
        self.logger.info(f"Failed: {summary['failed_tests']} ❌")
        self.logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        self.logger.info(f"Total Time: {summary['total_time']:.1f}s")
        
        if summary['total_errors'] > 0:
            self.logger.info(f"Total Errors: {summary['total_errors']} ❌")
        
        if summary['total_warnings'] > 0:
            self.logger.info(f"Total Warnings: {summary['total_warnings']} ⚠️")
        
        # Detailed results
        self.logger.info("\nDETAILED RESULTS:")
        for dataset, result in self.results.items():
            status = "✅ PASS" if result.get('overall_success') else "❌ FAIL"
            self.logger.info(f"  {dataset}: {status}")
            
            if result.get('database_info'):
                info = result['database_info']
                self.logger.info(f"    Size: {info.get('size_gb', 'Unknown')} GB")
                self.logger.info(f"    Patients: {info.get('patient_count', 'Unknown')}")
            
            if result.get('download_time'):
                self.logger.info(f"    Download: {result['download_time']:.1f}s")
            
            if result.get('conversion_time'):
                self.logger.info(f"    Conversion: {result['conversion_time']:.1f}s")
            
            if result.get('errors'):
                self.logger.info(f"    Errors: {len(result['errors'])}")
                for error in result['errors'][:3]:  # Show first 3 errors
                    self.logger.info(f"      - {error}")
                if len(result['errors']) > 3:
                    self.logger.info(f"      ... and {len(result['errors']) - 3} more")
        
        # Overall result
        overall_success = summary['failed_tests'] == 0
        overall_status = "🎉 ALL TESTS PASSED!" if overall_success else "💥 SOME TESTS FAILED!"
        self.logger.info(f"\n{overall_status}")
        self.logger.info("="*80)
    
    def save_results(self, output_file: Path = None):
        """Save test results to JSON file."""
        if output_file is None:
            output_file = Path("dataset_test_results.json")
        
        results_data = {
            'timestamp': time.time(),
            'summary': self._get_summary_stats(),
            'results': self.results
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(results_data, f, indent=2, default=str)
            self.logger.info(f"📄 Results saved to: {output_file}")
        except Exception as e:
            self.logger.error(f"❌ Failed to save results: {e}")


async def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="Run PhysioNet dataset tests")
    parser.add_argument(
        '--datasets', 
        nargs='+', 
        choices=['mimic-iv-demo', 'eicu-demo', 'all'],
        default=['all'],
        help='Datasets to test (default: all)'
    )
    parser.add_argument(
        '--test-data-root',
        type=Path,
        help='Root directory for test data (uses temp dirs if not specified)'
    )
    parser.add_argument(
        '--no-cleanup',
        action='store_true',
        help='Do not cleanup test data after tests'
    )
    parser.add_argument(
        '--output-file',
        type=Path,
        help='File to save test results (default: dataset_test_results.json)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle 'all' dataset selection
    datasets = args.datasets
    if 'all' in datasets:
        datasets = ['mimic-iv-demo', 'eicu-demo']
    
    # Create test runner
    test_runner = DatasetTestRunner(
        test_data_root=args.test_data_root,
        cleanup=not args.no_cleanup
    )
    
    # Set credentials if available
    if os.getenv('PHYSIONET_USERNAME') and os.getenv('PHYSIONET_PASSWORD'):
        test_runner.logger.info("✅ PhysioNet credentials found in environment")
    else:
        test_runner.logger.warning("⚠️  No PhysioNet credentials found - some tests may fail")
    
    try:
        # Run tests
        final_results = await test_runner.run_all_tests(datasets)
        
        # Save results
        test_runner.save_results(args.output_file)
        
        # Exit with appropriate code
        summary = final_results['summary']
        exit_code = 0 if summary['failed_tests'] == 0 else 1
        
        return exit_code
        
    except KeyboardInterrupt:
        test_runner.logger.info("🛑 Tests interrupted by user")
        return 130
    except Exception as e:
        test_runner.logger.error(f"💥 Test runner failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 