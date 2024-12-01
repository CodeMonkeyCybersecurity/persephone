Submodules which are used across scripts. This allows our code to be more modular.

## Calling up checkSudo.py
```
#!/usr/bin/env python3
import os
import sys  # Import sys to modify the Python path


# Add the parent directory of 'utils' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from utils.checkSudo import checkSudo

# Call the function from checkSudo.py early in the script
check_sudo()

... rest of your script ...
```
