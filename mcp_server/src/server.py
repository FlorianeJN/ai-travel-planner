import time
import sys


def main():
    print("MCP Dummy Server is alive", flush=True)
    try:
        # Keeps the container running without consuming CPU
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
