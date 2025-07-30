"""Entry point for running clinic_py as a module.

This module simply delegates to :func:`clinic_py.cli.main` when the
package is executed with ``python -m clinic_py``.
"""

from .cli import main

if __name__ == "__main__":
    main()