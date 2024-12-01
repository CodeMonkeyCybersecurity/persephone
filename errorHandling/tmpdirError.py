# Error handling for setting TMPDIR environment variable
try:
    tmp_dir = "/home/henry/tmp"
    
    # Check if /home/henry/tmp exists
    if os.path.exists(tmp_dir):
        # Run df -h to check disk space
        result = subprocess.run(['df', '-h', tmp_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            output = result.stdout
            logging.info(f"Disk space check for {tmp_dir}:\n{output}")
            print(f"Disk space check for {tmp_dir}:\n{output}")
            
            # Set TMPDIR if the directory exists and the command executed successfully
            os.environ["TMPDIR"] = tmp_dir
            logging.info(f"TMPDIR set to {tmp_dir}")
        else:
            logging.error(f"Error checking disk space: {result.stderr}")
            print(f"Error: Disk space check failed. {result.stderr}")
    else:
        raise FileNotFoundError(f"Temporary directory {tmp_dir} does not exist")
    
except Exception as e:
    logging.error(f"Failed to set TMPDIR: {e}")
    print(f"Error: Could not set TMPDIR. {e}")
