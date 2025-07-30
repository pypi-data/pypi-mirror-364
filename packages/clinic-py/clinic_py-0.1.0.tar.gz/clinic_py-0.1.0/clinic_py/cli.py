"""
Command‑line interface for clinic_py.

This module defines a ``main()`` function that is used as the entrypoint
when executing ``python -m clinic_py`` or ``clinic_py/cli.py``.  It
provides two subcommands:

``run``
    Launches a Python script under monitoring.  The script is executed
    in a separate interpreter process so that the monitoring thread
    collects metrics from the target.  Metrics are written to a binary
    file inside a ``.clinic_py`` directory next to the target script.

``serve``
    Launches a simple HTTP server that exposes a web dashboard for
    exploring the collected metrics.  Navigate to the given port
    (default 8000) in your browser to view charts and summaries.

The tool aims to support Python versions 3.9 through 3.12 and newer.
It avoids using features introduced in Python 3.13/3.14 such as
``profile.sample`` so that it can run on older interpreters.  The
sampling is performed in the C extension ``clinic_monitor``.
"""

from __future__ import annotations

import argparse
import os
import runpy
import subprocess
import sys
import struct
from pathlib import Path

# Plotly is used to generate interactive charts for the dashboard.
import plotly.graph_objects as go
import plotly.offline


def _run_target(script: str, outdir: str) -> None:
    """Run the target script under monitoring in a separate process.

    This helper function constructs a small bootstrap script that
    imports the ``clinic_monitor`` extension, starts sampling to a
    designated output file, executes the user's script via
    ``runpy.run_path`` and stops sampling when the script completes.

    Parameters
    ----------
    script: str
        The path to the Python script to execute.
    outdir: str
        Directory where the ``metrics.bin`` file will be written.  The
        directory is created if it does not already exist.
    """
    script_path = Path(script).resolve()
    out_dir = Path(outdir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_file = out_dir / "metrics.bin"
    # Build the bootstrap Python code to execute in the child process.
    # Pass the metrics filename to the extension so that it writes
    # binary records.  Use atexit to ensure sampling stops even if
    # the script raises an exception.
    bootstrap_code = (
        "import clinic_monitor, runpy, atexit, sys; "
        f"clinic_monitor.start(filepath=r'{metrics_file.as_posix()}'); "
        "atexit.register(clinic_monitor.stop); "
        f"runpy.run_path(r'{script_path.as_posix()}', run_name='__main__')"
    )
    # Inherit current PYTHONPATH but ensure that this package is on sys.path.
    env = os.environ.copy()
    # Prepend package root to PYTHONPATH so that clinic_monitor can be imported.
    pkg_root = Path(__file__).resolve().parent
    pkg_parent = str(pkg_root.parent)
    env.setdefault("PYTHONPATH", "")
    if env["PYTHONPATH"]:
        env["PYTHONPATH"] = pkg_parent + os.pathsep + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = pkg_parent
    cmd = [sys.executable, "-c", bootstrap_code]
    # Execute the script.  Propagate exit code.
    try:
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"Target script exited with code {exc.returncode}", file=sys.stderr)
        raise SystemExit(exc.returncode)


def _parse_records(metrics_path: Path) -> list[dict[str, float]]:
    """Parse the metrics binary file into a list of records.

    Each record is returned as a dictionary mapping field names to
    floats/ints.  If the file does not exist or cannot be parsed,
    returns an empty list.
    """
    if not metrics_path.exists():
        return []
    record_struct = struct.Struct('=dddllllllll')
    header_size = 64
    with metrics_path.open('rb') as f:
        data = f.read()
    if len(data) < header_size:
        return []
    records: list[dict[str, float]] = []
    keys = [
        'timestamp', 'user_time', 'system_time',
        'rss_kb', 'inblock', 'oublock', 'nvcsw', 'nivcsw',
        'py_app_frames', 'py_lib_frames', 'py_core_frames'
    ]
    offset = header_size
    while offset + record_struct.size <= len(data):
        unpacked = record_struct.unpack_from(data, offset)
        offset += record_struct.size
        rec_dict = {}
        for key, value in zip(keys, unpacked):
            rec_dict[key] = float(value)
        records.append(rec_dict)
    return records


def _serve_dashboard(outdir: str, port: int) -> None:
    """Serve a simple web dashboard to visualise the collected metrics.

    This function starts an HTTP server that serves a static HTML page
    and exposes API endpoints for retrieving the raw metric records
    and a summary.  Navigate to http://localhost:port/ in your web
    browser to view the dashboard.
    """
    metrics_path = Path(outdir) / "metrics.bin"
    records = _parse_records(metrics_path)
    # Precompute summary for efficiency
    summary = {}
    if records:
        for key in records[0].keys():
            summary[key] = max(r[key] for r in records)

    # HTML page with simple canvas-based plotting and table
    html_page = """<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <title>clinic_py Metrics Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    #chart { border: 1px solid #ccc; }
    table { border-collapse: collapse; margin-top: 20px; }
    th, td { border: 1px solid #ccc; padding: 4px 8px; }
    th { background: #eee; }
  </style>
</head>
<body>
  <h1>clinic_py Metrics Dashboard</h1>
  <canvas id='chart' width='800' height='300'></canvas>
  <div id='summary'></div>
  <script>
    async function fetchData() {
      const resp = await fetch('/api/records');
      const data = await resp.json();
      return data.records;
    }

    function drawChart(records) {
      const canvas = document.getElementById('chart');
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (!records.length) { return; }
      const n = records.length;
      // Extract series
      const ts = records.map(r => r.timestamp);
      const rss = records.map(r => r.rss_kb);
      const cpu = records.map(r => r.user_time + r.system_time);
      const memMax = Math.max(...rss);
      const cpuMax = Math.max(...cpu);
      const maxY = Math.max(memMax, cpuMax);
      const pad = 20;
      const w = canvas.width - pad * 2;
      const h = canvas.height - pad * 2;
      // Draw axes
      ctx.strokeStyle = '#000';
      ctx.beginPath();
      ctx.moveTo(pad, pad);
      ctx.lineTo(pad, pad + h);
      ctx.lineTo(pad + w, pad + h);
      ctx.stroke();
      // Helper to draw a line
      function drawLine(values, color) {
        ctx.strokeStyle = color;
        ctx.beginPath();
        for (let i = 0; i < n; i++) {
          const x = pad + (i / (n - 1)) * w;
          const y = pad + h - (values[i] / maxY) * h;
          if (i === 0) { ctx.moveTo(x, y); } else { ctx.lineTo(x, y); }
        }
        ctx.stroke();
      }
      drawLine(rss, '#007bff'); // memory in blue
      drawLine(cpu, '#ff5733'); // cpu in orange
    }

    function renderSummary(records) {
      if (!records.length) {
        document.getElementById('summary').innerText = 'No data available.';
        return;
      }
      const keys = Object.keys(records[0]);
      const maxima = {};
      for (const key of keys) { maxima[key] = -Infinity; }
      for (const rec of records) {
        for (const key of keys) { if (rec[key] > maxima[key]) maxima[key] = rec[key]; }
      }
      let html = '<h2>Summary (max values)</h2><table><tr>';
      for (const key of keys) { html += `<th>${key}</th>`; }
      html += '</tr><tr>';
      for (const key of keys) { html += `<td>${maxima[key].toFixed(2)}</td>`; }
      html += '</tr></table>';
      document.getElementById('summary').innerHTML = html;
    }

    async function init() {
      const records = await fetchData();
      drawChart(records);
      renderSummary(records);
    }
    init();
  </script>
</body>
</html>"""

    # --- Begin enhanced Plotly dashboard ---
    # Replace the simple canvas-based page with an interactive Plotly dashboard.
    # Only run if Plotly is available and there are records to display.
    if records:
        # Prepare time axis and metric series.  Memory is converted from KiB to MiB.
        ts = [r['timestamp'] for r in records]
        cpu_total = [r['user_time'] + r['system_time'] for r in records]
        rss_mb  = [r['rss_kb'] / 1024.0 for r in records]
        inblock = [r['inblock'] for r in records]
        oublock = [r['oublock'] for r in records]
        nvcsw   = [r['nvcsw'] for r in records]
        nivcsw  = [r['nivcsw'] for r in records]
        py_app  = [r.get('py_app_frames', 0.0) for r in records]
        py_lib  = [r.get('py_lib_frames', 0.0) for r in records]
        py_core = [r.get('py_core_frames', 0.0) for r in records]

        # Figure: CPU and memory (dual y-axis)
        fig_cpu_mem = go.Figure()
        fig_cpu_mem.add_trace(go.Scatter(x=ts, y=cpu_total, mode='lines', name='CPU Time (s)', line=dict(color='#ff5733')))
        fig_cpu_mem.add_trace(go.Scatter(x=ts, y=rss_mb, mode='lines', name='RSS (MiB)', line=dict(color='#007bff'), yaxis='y2'))
        fig_cpu_mem.update_layout(
            title="CPU Usage and Memory Consumption Over Time",
            xaxis_title="Time (s)",
            yaxis=dict(title="CPU Time (s)"),
            yaxis2=dict(title="RSS (MiB)", overlaying='y', side='right'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        # Figure: I/O blocks and context switches (dual y-axis)
        fig_io_context = go.Figure()
        fig_io_context.add_trace(go.Scatter(x=ts, y=inblock, mode='lines', name='inblock', line=dict(color='#1f77b4')))
        fig_io_context.add_trace(go.Scatter(x=ts, y=oublock, mode='lines', name='oublock', line=dict(color='#17becf')))
        fig_io_context.add_trace(go.Scatter(x=ts, y=nvcsw, mode='lines', name='nvcsw', line=dict(color='#2ca02c'), yaxis='y2'))
        fig_io_context.add_trace(go.Scatter(x=ts, y=nivcsw, mode='lines', name='nivcsw', line=dict(color='#d62728'), yaxis='y2'))
        fig_io_context.update_layout(
            title="I/O Blocks and Context Switches Over Time",
            xaxis_title="Time (s)",
            yaxis=dict(title="Block operations"),
            yaxis2=dict(title="Context switches", overlaying='y', side='right'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        # Figure: Python frame categories
        fig_frames = go.Figure()
        fig_frames.add_trace(go.Scatter(x=ts, y=py_app, mode='lines', name='App Frames', line=dict(color='#9467bd')))
        fig_frames.add_trace(go.Scatter(x=ts, y=py_lib, mode='lines', name='Lib Frames', line=dict(color='#8c564b')))
        fig_frames.add_trace(go.Scatter(x=ts, y=py_core, mode='lines', name='Core Frames', line=dict(color='#e377c2')))
        fig_frames.update_layout(
            title="Python Frame Categories Over Time",
            xaxis_title="Time (s)",
            yaxis_title="Frame count",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        # Generate HTML divs for each figure. Include Plotly.js only in the first figure.
        div_cpu_mem = plotly.offline.plot(fig_cpu_mem, include_plotlyjs='cdn', output_type='div')
        div_io_ctx  = plotly.offline.plot(fig_io_context, include_plotlyjs=False, output_type='div')
        div_frames  = plotly.offline.plot(fig_frames, include_plotlyjs=False, output_type='div')

        # Build summary table for maxima.
        summary_html = "<h2>Summary (max values)</h2>"
        if summary:
            headers = ''.join(f"<th>{k}</th>" for k in summary.keys())
            values  = ''.join(f"<td>{summary[k]:.2f}</td>" for k in summary.keys())
            summary_html += f"<table><tr>{headers}</tr><tr>{values}</tr></table>"
        else:
            summary_html += "<p>No data available.</p>"

        # Construct the new HTML page.
        html_page = f"""<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <title>clinic_py Metrics Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    .chart-container {{ margin-bottom: 40px; }}
    table {{ border-collapse: collapse; margin-top: 20px; }}
    th, td {{ border: 1px solid #ccc; padding: 4px 8px; }}
    th {{ background: #eee; }}
  </style>
</head>
<body>
  <h1>clinic_py Metrics Dashboard</h1>
  <div class='chart-container'>{div_cpu_mem}</div>
  <div class='chart-container'>{div_io_ctx}</div>
  <div class='chart-container'>{div_frames}</div>
  {summary_html}
</body>
</html>"""
    # --- End enhanced Plotly dashboard ---

    import http.server
    import json
    import socketserver

    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):  # type: ignore[override]
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html_page.encode('utf-8'))
            elif self.path == '/api/records':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'records': records}).encode('utf-8'))
            elif self.path == '/api/summary':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'summary': summary}).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()

    with socketserver.TCPServer(('', port), Handler) as httpd:
        sa = httpd.socket.getsockname()
        print(f"Serving clinic_py dashboard at http://{sa[0]}:{sa[1]}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="clinic_py",
        description="Simple Python CLI for non‑invasive performance metrics collection"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    # run subcommand
    run_parser = subparsers.add_parser(
        "run",
        help="Run a Python script under monitoring and collect metrics"
    )
    run_parser.add_argument(
        "script",
        help="Path to the Python script to profile"
    )
    run_parser.add_argument(
        "--outdir",
        default=".clinic_py",
        help="Directory where metrics will be written (default: .clinic_py)"
    )
    # serve subcommand
    serve_parser = subparsers.add_parser(
        "serve",
        help="Serve a web dashboard to explore collected metrics"
    )
    serve_parser.add_argument(
        "--outdir",
        default=".clinic_py",
        help="Directory where metrics were written (default: .clinic_py)"
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the dashboard server (default: 8000)"
    )
    args = parser.parse_args(argv)
    if args.command == "run":
        _run_target(args.script, args.outdir)
    elif args.command == "serve":
        _serve_dashboard(args.outdir, args.port)
    else:
        parser.error("Unknown command")


if __name__ == "__main__":
    main()