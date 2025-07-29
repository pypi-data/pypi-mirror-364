# src/utf_typecase/cli/main.py

import click
from utf_typecase.server import start_server
from utf_typecase.client import UTFClient
from utf_typecase.paste import Paster
from utf_typecase.interfaces import print_qr_grid
from utf_typecase.banner import print_banner_for_release
import threading
import time
import sys
from click_completion import init
from click_pwsh import support_pwsh_shell_completion
from utf_typecase import __version__

# Enable shell completion
init()
support_pwsh_shell_completion()


@click.command()
@click.option("--run-server", is_flag=True, help="Start the UTF server")
@click.option("--run-client", is_flag=True, help="Start the UTF client")
@click.option("--port", type=int, default=5000, help="Port to bind/connect to")
@click.option("--token", type=str, default="dev", help="Authentication token")
@click.option("--host", type=str, help="Remote server URL if client runs standalone")
@click.option("--qrcode", is_flag=True, help="network interface information")
@click.option(
    "--qrcode-inverted", is_flag=True, help="network interface information inverted"
)
@click.option(
    "--install-completion", is_flag=True, help="Install shell completion for your shell"
)
@click.version_option(version=__version__)
def main(
    run_server,
    run_client,
    port,
    token,
    host,
    qrcode,
    qrcode_inverted,
    install_completion,
):
    """Launch UTF Typecase server and/or client."""

    if install_completion:
        _install_completion()
        return

    print_banner_for_release(__version__, padding=1, align="left")

    if qrcode or qrcode_inverted:
        print("📡 Discoverable Flask Endpoints via QR Code:")
        print_qr_grid(port=port, border=2, invert=qrcode_inverted)

    if not run_server and not run_client:
        click.echo("❌ Nothing to run. Use --run-server and/or --run-client.")
        sys.exit(1)

    # 🧠 Require host if only client is running
    if run_client and not run_server and not host:
        click.echo("❌ Error: --host is required when running client alone.")
        sys.exit(1)

    # 🌐 Determine server base URL
    base_url = host or f"http://localhost:{port}"

    # 🧩 Launch server in separate thread if requested
    if run_server:
        click.echo(f"🧩 Starting server on port {port}...")
        server_thread = threading.Thread(
            target=start_server,
            kwargs={"port": port, "host": "0.0.0.0", "debug": False},
            daemon=True,
        )

        server_thread.start()

    # 🧲 Launch client if requested
    if run_client:
        click.echo(f"🧲 Starting client...")
        click.echo(f"🔐 Token: {token}")
        click.echo(f"🌐 Server URL: {base_url}\n")
        client = UTFClient(base_url, token, interval_ms=250)
        paster = Paster(delay_ms=60)
        client.on_data(lambda chars: paster.paste(chars))
        client.start()

        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            client.stop()
            click.echo("👋 Client stopped.")

    # 🧼 Keep server alive if client isn't running
    elif run_server:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            click.echo("👋 Server stopped.")


def _install_completion():
    import platform

    os_name = platform.system()
    click.echo("🔧 Installing shell completion...")

    if os_name == "Windows":
        click.echo("👉 Run this in PowerShell:")
        click.echo("python -m click_pwsh install utf-typecase Complete")
    else:
        click.echo("👉 Run this in your shell (Bash, Zsh, etc):")
        click.echo('eval "$(_UTF_TYPECASE_COMPLETE=bash_source utf-typecase)"')
        click.echo("💡 Add it to your shell config file to persist.")


if __name__ == "__main__":
    main()
