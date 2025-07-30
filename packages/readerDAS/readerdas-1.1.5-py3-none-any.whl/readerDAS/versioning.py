from packaging.version import Version, parse, InvalidVersion
from datetime import datetime


def parse_version(version: str) -> Version:
    try:
        version = parse(version)
    except InvalidVersion:
        try:
            date = datetime.strptime(version, "%d/%m/%Y")
            if date <= datetime(2024, 11, 17):
                version = Version("1.0.0")
            else:
                version = Version("1.2.0")
        except ValueError:
            version = Version("1.0.0")
    return version


def check_if_remove_steps(version: Version, default: bool) -> bool:

    return version < Version("1.2") and default


if __name__ == "__main__":
    version = parse_version(version="14/11/2024")
    print(version)
