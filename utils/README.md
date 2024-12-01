Submodules which are used across scripts. This allows our code to be more modular.

## Calling up checkSudo.py
```
#!/usr/bin/env python3

from utils.checkSudo import checkSudo

# Call the function from checkSudo.py early in the script
check_sudo()

def main():
    """Main function to execute the script logic."""
    print("Main script logic goes here.")

if __name__ == "__main__":
    main()
```
