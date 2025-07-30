"""
clinic_py package
=================

This package provides a CLI tool similar to Node's clinic.js for Python
applications.  It consists of a small C extension (`clinic_monitor`) that
periodically samples resource usage from the running process and a
Python-based command‑line interface that orchestrates launching a target
script, collecting metrics and rendering simple summaries.

The goal is to support Python 3.9 through 3.12 and beyond without
relying on bleeding‑edge features like ``profile.sample`` which only
appears in Python 3.15.  Instead, the collector uses the POSIX
``getrusage`` call (wrapped by the C library) to read metrics such as
CPU time, memory resident set size and I/O counters with minimal
overhead.  Measurements are written to a CSV file in a ``.clinic``
directory alongside the script being profiled.

For usage information run ``python -m clinic_py --help``.
"""

__all__ = ["cli"]