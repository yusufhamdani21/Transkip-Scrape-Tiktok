import sys
import traceback

LOG_FILE = "flet_test_log.txt"

with open(LOG_FILE, "w") as f:
    f.write("=== Flet Test Start ===\n")

try:
    import flet as ft
    with open(LOG_FILE, "a") as f:
        f.write(f"Flet version: {ft.__version__}\n")
        f.write("Import OK\n")
except Exception as e:
    with open(LOG_FILE, "a") as f:
        f.write(f"Import failed: {e}\n{traceback.format_exc()}\n")
    sys.exit(1)


def main(page: ft.Page):
    try:
        page.title = "Flet Test"
        page.add(ft.Text("Hello World!", size=30))
        with open(LOG_FILE, "a") as f:
            f.write("Page rendered OK\n")
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"main() error: {e}\n{traceback.format_exc()}\n")


if __name__ == "__main__":
    with open(LOG_FILE, "a") as f:
        f.write("Starting ft.app()...\n")
    try:
        ft.app(target=main)
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"ft.app() error: {e}\n{traceback.format_exc()}\n")
