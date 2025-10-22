from __future__ import annotations

from pathlib import Path

from app.gui import Application


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    app = Application(project_root)
    app.mainloop()


if __name__ == "__main__":
    main()
