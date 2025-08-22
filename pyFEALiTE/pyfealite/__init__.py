"""Top-level package for the local PyFEALiTE test package.

This initializer helps tests and examples import the *real* package
located at `pyFEALiTE/src/pyfealite` by adding the repository `src`
directory to `sys.path` when available. The change is performed
only at import-time and is safe during test collection.

We keep exports minimal to avoid accidental side-effects.
"""

from pathlib import Path
import sys

# If a development 'src' folder exists next to this package, prefer it so
# imports like `import pyfealite.plugins...` resolve to the real package.
_possible_src = Path(__file__).parent.parent / "src"
if _possible_src.exists():
	sys.path.insert(0, str(_possible_src))

# If the real package folder exists under the 'src' layout, add it to this
# package's __path__ so subpackages (for example `pyfealite.plugins`) can
# be imported even when this lightweight package is the first to be loaded
# during pytest collection.
_real_pkg = _possible_src / "pyfealite"
if _real_pkg.exists():
	# Append (not insert) so that the local package directory remains the
	# primary search location. This ensures subpackages added under the
	# test-level pyfealite folder (for example `plugins/pynite`) are found
	# before the src/pyfealite package content.
	__path__.append(str(_real_pkg))

__all__ = []
