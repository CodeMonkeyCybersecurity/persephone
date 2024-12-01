# Error handling for setting the BORG_RSH environment variable
try:
    ssh_key_path = os.path.expanduser("~/.ssh/id_ed25519")
    if os.path.exists(ssh_key_path):
        os.environ["BORG_RSH"] = f"ssh -i {ssh_key_path}"
        logging.info(f"BORG_RSH set to use SSH key: {ssh_key_path}")
    else:
        raise FileNotFoundError(f"SSH key not found at {ssh_key_path}")
except Exception as e:
    logging.error(f"Failed to set BORG_RSH: {e}")
    print(f"Error: Could not set BORG_RSH. {e}")
