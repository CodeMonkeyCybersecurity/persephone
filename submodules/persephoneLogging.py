import logging

# Set up logging configuration
logging.basicConfig(
    filename="/var/log/cybermonkey/persephone.log", 
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def example_submodule_function():
    try:
        # Code logic
        logging.info("Submodule function executed successfully.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise
