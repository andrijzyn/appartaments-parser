import tomllib
from pathlib import Path
from . import driver

driver = driver.initiate()
driver.get("https://www.njuskalo.hr/")

try:
    config = tomllib.loads(Path("config.toml").read_text())
except FileNotFoundError:
    print("Where config?")