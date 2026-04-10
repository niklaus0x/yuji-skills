#!/usr/bin/env python3
"""
with_server.py — Server Lifecycle Manager
Starts one or more servers, waits for them to be ready, runs a command, then tears down.

Usage:
  python scripts/with_server.py --server "npm run dev" --port 3000 -- python test.py
  python scripts/with_server.py \\
    --server "cd backend && python server.py" --port 3000 \\
    --server "cd frontend && npm run dev" --port 5173 \\
    -- python test.py
"""
import argparse
import subprocess
import sys
import time
import socket
import signal
import os

running_procs = []


def wait_for_port(port: int, host='localhost', timeout=60) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (socket.error, ConnectionRefusedError):
            time.sleep(0.5)
    return False


def start_server(command: str, port: int, timeout: int = 60) -> subprocess.Popen:
    print(f'🚀 Starting server on port {port}: {command}')
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    running_procs.append(proc)
    if wait_for_port(port, timeout=timeout):
        print(f'✅ Server ready on port {port}')
    else:
        print(f'❌ Server on port {port} did not start in {timeout}s', file=sys.stderr)
        cleanup()
        sys.exit(1)
    return proc


def cleanup():
    for proc in running_procs:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description='Start servers and run a command')
    parser.add_argument('--server', action='append', default=[], help='Server start command')
    parser.add_argument('--port', action='append', type=int, default=[], help='Port to wait on')
    parser.add_argument('--timeout', type=int, default=60, help='Timeout waiting for server (seconds)')
    parser.add_argument('cmd', nargs=argparse.REMAINDER, help='Command to run after servers start')
    args = parser.parse_args()

    if len(args.server) != len(args.port):
        print('Error: --server and --port must be paired', file=sys.stderr)
        sys.exit(1)

    try:
        for server_cmd, port in zip(args.server, args.port):
            start_server(server_cmd, port, timeout=args.timeout)

        cmd = [c for c in args.cmd if c != '--']
        if not cmd:
            print('No command specified. Servers running. Ctrl+C to stop.')
            signal.pause()
        else:
            print(f'\n▶ Running: {" ".join(cmd)}\n')
            result = subprocess.run(cmd)
            sys.exit(result.returncode)
    finally:
        cleanup()


if __name__ == '__main__':
    main()
