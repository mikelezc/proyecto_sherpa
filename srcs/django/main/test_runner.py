"""
Custom Test Runner for Task Management System
Provides colored output for better test result visualization
"""
import sys
from django.test.runner import DiscoverRunner


class ColoredTestRunner(DiscoverRunner):
    """Custom test runner with colored output"""
    
    def run_tests(self, test_labels, **kwargs):
        """Run tests with colored output and better formatting"""
        
        # Print header
        print(f"\n\033[96m🧪 Task Management System - Test Suite\033[0m")
        print(f"\033[96m{'='*55}\033[0m")
        
        # Run the actual tests
        result = super().run_tests(test_labels, **kwargs)
        
        # No footer here - let the shell script handle it
        return result
