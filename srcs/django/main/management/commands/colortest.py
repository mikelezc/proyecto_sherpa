"""
Colored Test Command for Task Management System
Runs tests with enhanced colored output
"""
import subprocess
import sys
import re
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run tests with colored output'

    def add_arguments(self, parser):
        parser.add_argument(
            'test_labels',
            nargs='*',
            help='Test labels to run (e.g., tests.test_models)',
        )
        parser.add_argument(
            '--verbosity', '-v',
            action='store',
            dest='verbosity',
            default=2,
            type=int,
            help='Verbosity level',
        )
        parser.add_argument(
            '--pattern',
            action='store',
            dest='pattern',
            default='test*.py',
            help='Test discovery pattern',
        )

    def handle(self, *args, **options):
        # Colors for terminal output
        colors = {
            'HEADER': '\033[95m',
            'BLUE': '\033[94m',
            'CYAN': '\033[96m',
            'GREEN': '\033[92m',
            'YELLOW': '\033[93m',
            'RED': '\033[91m',
            'BOLD': '\033[1m',
            'UNDERLINE': '\033[4m',
            'END': '\033[0m'
        }

        # Print header
        self.stdout.write(f"\n{colors['CYAN']}🧪 Task Management System - Test Suite{colors['END']}")
        self.stdout.write(f"{colors['CYAN']}{'='*60}{colors['END']}\n")

        # Build test command
        test_labels = options['test_labels'] or []
        cmd = [
            sys.executable, 'manage.py', 'test',
            f"--verbosity={options['verbosity']}",
            f"--pattern={options['pattern']}"
        ] + test_labels

        # Run tests and capture output
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Process output line by line and add colors
            for line in iter(process.stdout.readline, ''):
                if line:
                    colored_line = self.colorize_line(line, colors)
                    self.stdout.write(colored_line, ending='')

            process.wait()
            exit_code = process.returncode

            # Print summary
            self.stdout.write(f"\n{colors['CYAN']}{'='*60}{colors['END']}")
            if exit_code == 0:
                self.stdout.write(f"{colors['GREEN']}{colors['BOLD']}🎉 ALL TESTS PASSED! System ready for production 🎉{colors['END']}")
            else:
                self.stdout.write(f"{colors['RED']}{colors['BOLD']}❌ {exit_code} test(s) failed. Review output above.{colors['END']}")
            self.stdout.write(f"{colors['CYAN']}{'='*60}{colors['END']}\n")

            return exit_code

        except KeyboardInterrupt:
            self.stdout.write(f"\n{colors['YELLOW']}⚠️ Tests interrupted by user{colors['END']}")
            return 1
        except Exception as e:
            self.stdout.write(f"\n{colors['RED']}❌ Error running tests: {e}{colors['END']}")
            return 1

    def colorize_line(self, line, colors):
        """Apply colors to test output lines"""
        
        # Test results
        if ' ... ok' in line:
            line = line.replace(' ... ok', f" ... {colors['GREEN']}✅ OK{colors['END']}")
        elif ' ... ERROR' in line:
            line = line.replace(' ... ERROR', f" ... {colors['RED']}❌ ERROR{colors['END']}")
        elif ' ... FAIL' in line:
            line = line.replace(' ... FAIL', f" ... {colors['RED']}❌ FAIL{colors['END']}")
        
        # Test names (start with test_)
        elif line.strip().startswith('test_'):
            # Extract test name and color it
            test_match = re.match(r'^(test_\w+)', line.strip())
            if test_match:
                test_name = test_match.group(1)
                line = line.replace(test_name, f"{colors['BLUE']}{test_name}{colors['END']}", 1)
        
        # Warnings and errors in output
        elif 'WARNING' in line and not line.startswith('test_'):
            line = line.replace('WARNING', f"{colors['YELLOW']}⚠️ WARNING{colors['END']}")
        elif 'ERROR' in line and not line.startswith('test_'):
            line = line.replace('ERROR', f"{colors['RED']}❌ ERROR{colors['END']}")
        elif 'INFO' in line and not line.startswith('test_'):
            line = line.replace('INFO', f"{colors['CYAN']}ℹ️ INFO{colors['END']}")
        
        # System messages
        elif 'Found' in line and 'test(s)' in line:
            line = f"{colors['CYAN']}{line}{colors['END']}"
        elif 'Creating test database' in line:
            line = f"{colors['CYAN']}{line}{colors['END']}"
        elif 'Destroying test database' in line:
            line = f"{colors['CYAN']}{line}{colors['END']}"
        elif 'System check identified' in line:
            line = f"{colors['GREEN']}{line}{colors['END']}"
        elif 'Operations to perform' in line or 'Applying' in line:
            line = f"{colors['CYAN']}{line}{colors['END']}"
        
        # Final results
        elif 'Ran' in line and 'tests in' in line:
            if 'FAILED' in line:
                line = f"{colors['RED']}{line}{colors['END']}"
            else:
                line = f"{colors['GREEN']}{line}{colors['END']}"
        
        return line
