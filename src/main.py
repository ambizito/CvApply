from __future__ import annotations

from pathlib import Path

from app import Application


def reset_environment(project_root: Path) -> None:
    """Remove persisted state so the app behaves like the first launch."""

    storage_path = project_root / "storage" / "webkit_profile"
    env_path = project_root / ".env"

    if storage_path.exists():
        import shutil

        shutil.rmtree(storage_path)

    if env_path.exists():
        env_path.unlink()


def main(test_mode: bool = False) -> None:
    project_root = Path(__file__).resolve().parent.parent
    if test_mode:
        reset_environment(project_root)
    app = Application(project_root)
    app.mainloop()


if __name__ == "__main__":
    import sys

    test_mode = len(sys.argv) > 1 and sys.argv[1] == "-test"
    main(test_mode)
