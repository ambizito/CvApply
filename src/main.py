from __future__ import annotations

from pathlib import Path

from app.gui import Application



def reset_storage(project_root: Path):
    storage_path = project_root / "storage" / "webkit_profile"
    if storage_path.exists():
        import shutil
        shutil.rmtree(storage_path)

def main(test_mode: bool = False) -> None:
    project_root = Path(__file__).resolve().parent.parent
    if test_mode:
        reset_storage(project_root)
    app = Application(project_root)
    app.mainloop()


if __name__ == "__main__":
    import sys
    test_mode = len(sys.argv) > 1 and sys.argv[1] == "-test"
    main(test_mode)
