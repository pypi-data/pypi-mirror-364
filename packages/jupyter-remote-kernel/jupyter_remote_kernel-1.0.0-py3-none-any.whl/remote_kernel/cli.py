#!/usr/bin/env python3
import sys
import os
import json
import subprocess
import signal
import shutil
import logging

REMOTE_CONN_DIR = "/tmp"
PID_FILE = "/tmp/remote_kernel.pid"
KERNELS_DIR = os.path.expanduser("~/.local/share/jupyter/kernels")

logging.basicConfig(
    level=logging.INFO,
    format="[remote_kernel] %(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def parse_endpoint(endpoint):
    """Parse endpoint string into host and port."""
    if ":" in endpoint:
        host, port = endpoint.split(":", 1)
        try:
            port = int(port)
        except ValueError:
            logging.error(f"Invalid port in endpoint: {endpoint}")
            sys.exit(1)
        return host, port
    return endpoint, None

def sync_file(src, endpoint, port, dest):
    """Sync a file to the remote endpoint using rsync over SSH."""
    cmd = ["rsync", "-az", "--inplace"]
    if port:
        cmd += ["-e", f"ssh -p {port}"]
    cmd += [src, f"{endpoint}:{dest}"]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to sync file: {e}")
        sys.exit(1)

def get_remote_python(host, port):
    """Detect the remote python interpreter path."""
    env_path = os.environ.get("REMOTE_KERNEL_PYTHON")
    if env_path:
        return env_path
    ssh_cmd = ["ssh"]
    if port:
        ssh_cmd += ["-p", str(port)]
    ssh_cmd += [host, "which python3 || which python"]
    try:
        out = subprocess.check_output(ssh_cmd, text=True, timeout=10).strip()
        if out:
            return out.splitlines()[0]
    except Exception as e:
        logging.warning(f"Could not detect remote python: {e}")
    return "python"

def get_ssh_command():
    """Return autossh if available, else ssh and print suggestion."""
    try:
        subprocess.check_output(["which", "autossh"], stderr=subprocess.DEVNULL)
        return "autossh"
    except Exception:
        print("[remote_kernel] INFO: 'autossh' not found, falling back to 'ssh'. For better reliability, install autossh (sudo apt install autossh).")
        return "ssh"

def start_kernel(endpoint, conn_file):
    """Start the remote kernel via SSH and port forwarding."""
    if not os.path.exists(conn_file):
        logging.error(f"Connection file not found: {conn_file}")
        sys.exit(1)

    host, port = parse_endpoint(endpoint)
    remote_python = get_remote_python(host, port)
    try:
        with open(conn_file) as f:
            cfg = json.load(f)
        ports = [cfg[k] for k in ("shell_port", "iopub_port", "stdin_port", "control_port", "hb_port")]
    except Exception as e:
        logging.error(f"Failed to read connection file: {e}")
        sys.exit(1)

    remote_conn_file = f"{REMOTE_CONN_DIR}/{os.path.basename(conn_file)}"
    sync_file(conn_file, host, port, remote_conn_file)

    forwards = []
    for p in ports:
        forwards += ["-L", f"{p}:localhost:{p}"]

    ssh_bin = get_ssh_command()
    ssh_cmd = [ssh_bin, "-o", "ExitOnForwardFailure=yes", "-o", "ServerAliveInterval=30"]
    if port:
        ssh_cmd += ["-p", str(port)]
    ssh_cmd += forwards + [host, f"{remote_python} -m ipykernel_launcher -f {remote_conn_file}"]

    logging.info(f"Synced connection file -> {remote_conn_file}")
    logging.info(f"Starting remote kernel on {host}, forwarding ports {ports}")

    try:
        proc = subprocess.Popen(ssh_cmd)
    except Exception as e:
        logging.error(f"Failed to start SSH process: {e}")
        sys.exit(1)

    try:
        with open(PID_FILE, "w") as pf:
            pf.write(str(proc.pid))
    except Exception as e:
        logging.error(f"Failed to write PID file: {e}")
        proc.terminate()
        sys.exit(1)

    try:
        proc.wait()
    except KeyboardInterrupt:
        logging.info("Interrupted, shutting down...")
        proc.terminate()
        proc.wait()
    finally:
        if os.path.exists(PID_FILE):
            try:
                os.remove(PID_FILE)
            except Exception:
                pass

def kill_kernel():
    """Kill the running SSH tunnel/kernel process."""
    if not os.path.exists(PID_FILE):
        logging.info("No running tunnel found.")
        return

    try:
        with open(PID_FILE) as pf:
            pid = int(pf.read().strip())
        os.kill(pid, signal.SIGTERM)
        logging.info(f"Terminated SSH process (PID {pid}).")
    except ProcessLookupError:
        logging.info("Process already stopped.")
    except Exception as e:
        logging.error(f"Failed to kill process: {e}")
    finally:
        try:
            os.remove(PID_FILE)
        except Exception:
            pass

def add_kernel(endpoint, name):
    """Add a new Jupyter kernel spec for a remote endpoint."""
    try:
        abs_path = subprocess.check_output(["which", "remote_kernel"], text=True).strip()
    except subprocess.CalledProcessError:
        logging.error("'remote_kernel' not in PATH. Install with pip first.")
        sys.exit(1)

    slug = name.lower().replace(" ", "_")
    kernel_dir = os.path.join(KERNELS_DIR, slug)
    try:
        os.makedirs(kernel_dir, exist_ok=True)
    except Exception as e:
        logging.error(f"Failed to create kernel directory: {e}")
        sys.exit(1)

    kernel_json = {
        "argv": [
            abs_path,
            "--endpoint", endpoint,
            "-f", "{connection_file}"
        ],
        "display_name": name,
        "language": "python"
    }

    try:
        with open(os.path.join(kernel_dir, "kernel.json"), "w") as f:
            json.dump(kernel_json, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to write kernel.json: {e}")
        sys.exit(1)

    logging.info(f"Added kernel: {name} ({endpoint})")
    logging.info(f"Location: {kernel_dir}")

def list_kernels():
    """List all installed remote kernels."""
    if not os.path.exists(KERNELS_DIR):
        logging.info("No kernels installed.")
        return

    for slug in os.listdir(KERNELS_DIR):
        kdir = os.path.join(KERNELS_DIR, slug)
        kjson = os.path.join(kdir, "kernel.json")
        if not os.path.isfile(kjson):
            continue
        try:
            with open(kjson) as f:
                data = json.load(f)
            name = data.get("display_name", slug)
            argv = data.get("argv", [])
            endpoint = None
            if "--endpoint" in argv:
                endpoint = argv[argv.index("--endpoint") + 1]

            print(f"slug: {slug}")
            print(f"  name: {name}")
            if endpoint:
                print(f"  endpoint: {endpoint}")
            print("---")
        except Exception as e:
            logging.warning(f"Failed to read kernel spec {kjson}: {e}")

def delete_kernel(name_or_slug):
    """Delete a remote kernel spec by name or slug."""
    slug = name_or_slug.lower().replace(" ", "_")
    kernel_dir = os.path.join(KERNELS_DIR, slug)
    if not os.path.exists(kernel_dir):
        logging.info(f"Kernel '{name_or_slug}' not found.")
        return
    try:
        shutil.rmtree(kernel_dir)
        logging.info(f"Deleted kernel '{name_or_slug}'.")
    except Exception as e:
        logging.error(f"Failed to delete kernel '{name_or_slug}': {e}")

def print_usage():
    print("Usage:")
    print("  remote_kernel add --endpoint <user@host[:port]> --name <Display Name>")
    print("  remote_kernel list")
    print("  remote_kernel delete <slug-or-display-name>")
    print("  remote_kernel --kill")
    print("  remote_kernel --endpoint <user@host[:port]> -f <connection_file>")

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    if "add" in sys.argv:
        if "--endpoint" not in sys.argv or "--name" not in sys.argv:
            print_usage()
            sys.exit(1)
        endpoint = sys.argv[sys.argv.index("--endpoint") + 1]
        name = sys.argv[sys.argv.index("--name") + 1]
        add_kernel(endpoint, name)
        return

    if "list" in sys.argv:
        list_kernels()
        return

    if "delete" in sys.argv:
        if len(sys.argv) < 3:
            print_usage()
            sys.exit(1)
        target = sys.argv[2]
        delete_kernel(target)
        return

    if "--kill" in sys.argv:
        kill_kernel()
        return

    if "--endpoint" not in sys.argv or "-f" not in sys.argv:
        print_usage()
        sys.exit(1)

    endpoint = sys.argv[sys.argv.index("--endpoint") + 1]
    conn_file = sys.argv[sys.argv.index("-f") + 1]
    start_kernel(endpoint, conn_file)

if __name__ == "__main__":
    main()
