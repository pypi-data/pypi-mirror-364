import utf_typecase.interfaces as interfaces
import netifaces
import shutil
from unittest.mock import patch


def test_generate_qr_ascii_block_format():
    url = "http://192.168.0.100:5000"
    qr_lines = interfaces.generate_qr_ascii_block(url)
    assert qr_lines
    assert all(isinstance(line, str) for line in qr_lines)
    assert "http://" in "".join(qr_lines)


@patch("netifaces.interfaces")
@patch("netifaces.ifaddresses")
def test_get_filtered_ipv4_addresses(mock_ifaddresses, mock_interfaces):
    mock_interfaces.return_value = ["lo", "eth0"]
    mock_ifaddresses.side_effect = lambda iface: {
        netifaces.AF_INET: (
            [{"addr": "127.0.0.1"}]
            if iface == "lo"
            else [{"addr": "192.168.1.55"}, {"addr": "172.20.10.1"}]
        )
    }

    result = interfaces.get_filtered_ipv4_addresses()
    assert result == ["192.168.1.55"]  # Excludes 127.* and 172.*


@patch(
    "interfaces.get_filtered_ipv4_addresses", return_value=["10.0.0.2", "192.168.1.100"]
)
@patch("shutil.get_terminal_size")
def test_print_qr_grid_does_not_crash(mock_terminal_size, mock_ip_fetcher):
    mock_terminal_size.return_value = shutil.os.terminal_size((120, 24))

    # Just ensure it runs without exceptions
    try:
        interfaces.print_qr_grid(port=5000, border=1, invert=False)
    except Exception as e:
        assert False, f"print_qr_grid raised an exception: {e}"
