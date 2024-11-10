import sys

def example_submodule_function():
    try:
        # Some code that might throw an error
        pass
    except FileNotFoundError as e:
        print(f"Error: {e}")
        # Optional: re-raise the error or exit if it’s critical
        sys.exit(1)
