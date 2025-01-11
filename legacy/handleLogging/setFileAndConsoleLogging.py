# Set up logging to output to both a file and the console
file_handler = logging.FileHandler("/var/log/eos.log")
file_handler.setLevel(logging.DEBUG)  # Log all levels to the log file

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)  # Only log errors or higher to the console

logging.basicConfig(
    level=logging.DEBUG,  # Overall log level
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[file_handler, console_handler]
)
