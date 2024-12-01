# Create a repository
def createBorgRepo(config):
    """Initialize a new Borg repository."""
    try:
        repo = config['borg']['repo']
        passphrase = config['borg']['passphrase']
        
        # Set up environment for Borg init
        env = os.environ.copy()
        env['BORG_PASSPHRASE'] = passphrase
        
        # Initialize the repository with encryption if set
        encryption_type = config['borg'].get('encryption', 'repokey')

        # Run Borg init command
        borg_init_cmd = ['borg', 'init', '--encryption', encryption_type, repo]
        result = subprocess.run(borg_init_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True)

        logging.info(f"Repository {repo} created successfully.")
        print(f"Repository {repo} created successfully.")  # Success message
        return True  # Indicate success
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to create Borg repository: {e.stderr}")
        print(f"Error: Failed to create repository {repo}. {e.stderr}")  # Failure message
        return False  # Indicate failure
