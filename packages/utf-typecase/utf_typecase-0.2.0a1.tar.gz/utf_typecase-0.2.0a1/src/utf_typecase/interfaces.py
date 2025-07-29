# interfaces.py

import socket
import shutil
import qrcode
from io import StringIO

import netifaces


def get_filtered_ipv4_addresses():
    ips = []
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        for info in addrs.get(netifaces.AF_INET, []):
            ip = info.get("addr")
            if ip and not (ip.startswith("127.") or ip.startswith("172.")):
                ips.append(ip)
    return ips


def generate_qr_ascii_block(data, border=4, invert=False):
    """Generate QR code and return its ASCII representation as lines."""
    qr = qrcode.QRCode(border=border)
    qr.add_data(data)
    qr.make(fit=True)

    buf = StringIO()
    qr.print_ascii(out=buf, invert=invert)
    buf.seek(0)
    return buf.read().splitlines()


def print_qr_grid(port=5000, border=2, invert=False):
    """Print multiple QR codes side-by-side with IP labels, based on terminal width."""
    ips = get_filtered_ipv4_addresses()
    # ips = get_local_ipv4_addresses()
    qr_blocks = []
    labels = []

    for ip in ips:
        url = f"http://{ip}:{port}"
        block = generate_qr_ascii_block(url, border=border, invert=invert)
        label = f" {url} "
        qr_blocks.append(block)
        labels.append(label)

    # Calculate max height of QR blocks
    height = max(len(b) for b in qr_blocks)
    width = max(len(line) for block in qr_blocks for line in block)

    term_width = shutil.get_terminal_size((80, 24)).columns
    block_with_padding = width + 2
    columns = max(1, term_width // block_with_padding)

    # Print in rows of 'columns' QR blocks
    for row_start in range(0, len(qr_blocks), columns):
        row_blocks = qr_blocks[row_start : row_start + columns]
        row_labels = labels[row_start : row_start + columns]
        max_block_height = max(len(b) for b in row_blocks)

        # Pad blocks to equal height
        row_blocks = [
            b + [" " * width] * (max_block_height - len(b)) for b in row_blocks
        ]

        # Print QR code lines side-by-side
        for line_index in range(max_block_height):
            row_line = "  ".join(block[line_index] for block in row_blocks)
            print(row_line)

        # Print labels underneath each QR code
        print("  ".join(label.center(width) for label in row_labels))
        print()  # Spacer between rows


# For quick testing: run with 'python src/utf_typecase/interfaces.py'
if __name__ == "__main__":
    from interfaces import print_qr_grid

    print("📡 Discoverable Flask Endpoints via QR Code:")
    print_qr_grid(port=5000, border=2, invert=False)
