"""Main entry point for the LF data UI tool."""

from lfdata.ui.app import LFDataUIApp


def main() -> None:
    """Launches the LF data UI application."""
    app = LFDataUIApp()
    app.mainloop()


if __name__ == '__main__':
    main()
