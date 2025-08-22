"""Utility script for running a single test manually.

This file intentionally avoids executing test functions at import time so
pytest can safely collect test modules. Use `python run_single_test.py` to
run ad-hoc tests when needed.
"""

def main():
	print("run_single_test helper - no-op when imported by pytest.")


if __name__ == "__main__":
	main()
