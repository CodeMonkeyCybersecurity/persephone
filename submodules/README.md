Submodules which are used across scripts. This allows our code to be more modular.

## Calling up checkSudo.py
```
#!/usr/bin/env python3

from checkSudo import checkSudo

def main():
    """Main function to execute the script logic."""
    check_sudo()  # Call the function from checkSudo.py
    print("Main script logic goes here.")

if __name__ == "__main__":
    main()
```
