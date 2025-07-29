import importlib
import pkgutil
import sys
import pathlib
import tomllib
from typing import Any, Dict


def load_config() -> Dict[str, Any] | None:
    current_dir = pathlib.Path.cwd()
    config_path = current_dir / "zenx.toml"
    if config_path.exists():
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
            return config


def discover_local_spiders():
    config = load_config()
    if not config:
        return
    project_root = pathlib.Path.cwd()
    project_name: str | Any = config.get("project")
    spiders_dir = project_root / project_name / "spiders"
    
    if not spiders_dir.is_dir():
        return

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    try:
        spiders_module = importlib.import_module(f"{project_name}.spiders")
        for _,name,_ in pkgutil.iter_modules(spiders_module.__path__):
            importlib.import_module(f".{name}", spiders_module.__name__)
    except ImportError:
        pass
