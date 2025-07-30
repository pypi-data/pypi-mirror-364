# clinic-py

Non-invasive performance metrics collection for Python applications, inspired by Node.js clinic.

## Features

- **Non-invasive monitoring**: Collect performance metrics without modifying your code
- **System metrics**: CPU usage, memory consumption, I/O operations, context switches
- **Python stack analysis**: Categorize frames into application, library, and core code
- **Binary metrics format**: Efficient storage and parsing of performance data
- **Web dashboard**: Interactive visualization of collected metrics
- **Cross-platform**: Supports Linux, macOS, and other Unix-like systems

## Installation

```bash
pip install clinic-py
```

## Quick Start

### Monitor a Python script

```bash
python -m clinic_py run your_script.py
```

This will execute your script and collect performance metrics in the `.clinic_py/` directory.

### View results in web dashboard

```bash
python -m clinic_py serve
```

Then open http://localhost:8000 in your browser to explore the performance data.

## Usage

### Command Line Interface

```bash
# Run a script under monitoring
python -m clinic_py run [--outdir DIR] script.py

# Serve web dashboard
python -m clinic_py serve [--outdir DIR] [--port PORT]
```

### Options

- `--outdir`: Directory where metrics are stored (default: `.clinic_py`)
- `--port`: Port for the web dashboard (default: 8000)

## How it Works

clinic-py uses a C extension to periodically sample system resources with minimal overhead:

1. **Resource Sampling**: Collects CPU time, memory usage, I/O counters using `getrusage()`
2. **Stack Sampling**: Analyzes Python call stacks to categorize code execution
3. **Binary Storage**: Writes metrics to efficient binary format
4. **Web Visualization**: Provides interactive charts and summaries

## Requirements

- Python 3.9+
- Unix-like operating system (Linux, macOS, etc.)
- C compiler for building the extension

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.