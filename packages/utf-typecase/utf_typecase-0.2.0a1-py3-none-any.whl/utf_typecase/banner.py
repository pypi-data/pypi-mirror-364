import shutil
import textwrap

BANNERS = {
    "v0.2.0": """
+---------------------------------------------------------------------------+
|                            utf-typecase v0.2.0                            |
=============================================================================
|1 2 3 4 5 6 7 8 9 0 + -|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
""",
    "v0.3.0": """
+---------------------------------------------------------------------------+
|                            utf-typecase v0.3.0                            |
=============================================================================
|1 2 3 4 5 6 7 8 9 0 + -|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
""",
}


def print_banner(banner: str, padding: int = 2, align: str = "center"):
    term_width = shutil.get_terminal_size((80, 24)).columns
    max_width = term_width - padding * 2

    lines = banner.strip().splitlines()
    wrapped = [textwrap.fill(line, width=max_width) for line in lines]
    for line in wrapped:
        if align == "center":
            print(" " * padding + line.center(max_width))
        elif align == "right":
            print(" " * padding + line.rjust(max_width))
        else:
            print(" " * padding + line.ljust(max_width))


def print_banner_for_release(tag: str, **kwargs):
    banner = BANNERS.get(tag)
    if banner:
        print_banner(banner, **kwargs)
    else:
        print(f"🚫 No banner found for release '{tag}'")


# For quick testing: run with 'python src/utf_typecase/banner.py'
if __name__ == "__main__":
    # https://en.perfcode.com/tools/generator/ascii-art
    # ANSI Shadow
    # ToDo: Fix problem with leading spaces in the banner
    ascii_banner = """
 ██████╗ ███╗   ██╗██╗   ██╗
██╔════╝ ████╗  ██║██║   ██║
██║  ███╗██╔██╗ ██║██║   ██║
██║   ██║██║╚██╗██║██║   ██║
╚██████╔╝██║ ╚████║╚██████╔╝
 ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ 
"""
    print_banner(ascii_banner, padding=4, align="left")
    print_banner_for_release("v0.2.0", padding=1, align="left")
    print_banner_for_release("v0.3.0", padding=1, align="left")
    print_banner_for_release("v1.0.0", padding=1, align="left")
