from pathlib import Path


def resolve_output_path(
    target_path: str | Path, 
    default_subfolder: str = ""
) -> Path:

    path = Path(target_path)

    if not path.is_absolute():
        if len(path.parts) == 1 and default_subfolder:
            base_dir = Path.cwd() / "results" / default_subfolder
        else:
            base_dir = Path.cwd()
            
        path = base_dir / path

    path.parent.mkdir(parents=True, exist_ok=True)
    return path