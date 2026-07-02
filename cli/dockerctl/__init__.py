"""dockerctl: a small, non-interactive Docker helper CLI for CI/CD."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("dockerctl")
except PackageNotFoundError:  # running from a source tree without install
    __version__ = "0.0.0+unknown"
