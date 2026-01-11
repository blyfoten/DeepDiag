"""
DeepDiag - ELM327 Diagnostic Application
Entry point for the application.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from gui.app import DiagnosticApp


def main():
    """Main entry point."""
    print("DeepDiag - ELM327 Diagnostic Tool")
    print("Starting application...")

    # Create and run application
    app = DiagnosticApp()
    app.create_gui()
    app.run()

    print("Application closed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
