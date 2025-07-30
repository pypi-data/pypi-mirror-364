import argparse
from .math_genie_calc_mcp_server_v1 import mcp
def main():
    """MCP Wiki kel: Read Wikipedia articles and convert them to Markdown."""
    parser = argparse.ArgumentParser(
        description="Gives you the ability to read Wikipedia articles and convert them to Markdown."
    )
    parser.parse_args()
    mcp.run()


if __name__ == "__main__":
    main()