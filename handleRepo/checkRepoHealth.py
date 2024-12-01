# Check the repository
def check_repo(config):
    """Check repository health with 'borg check'."""
    repo = config['borg']['repo']
    passphrase = config['borg']['passphrase']

    env = os.environ.copy()
    env['BORG_PASSPHRASE'] = passphrase

    try:
        result = subprocess.run(['borg', 'check', repo], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True)
        logging.info(result.stdout)
        print(f"Repository check passed for {repo}.")  # Success message
        return True  # Indicate success
    except subprocess.CalledProcessError as e:
        logging.error(f"Repository check failed: {e.stderr}")
        print(f"Error: Repository check failed for {repo}. {e.stderr}")  # Failure message
        return False  # Indicate failure
