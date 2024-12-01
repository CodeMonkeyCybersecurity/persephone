// Load or create the configuration file
async function loadOrCreateConfig() {
  let config;
  try {
    await fs.access(CONFIG_PATH);  // Check if file exists
    const content = await fs.readFile(CONFIG_PATH, 'utf8');
    config = yaml.load(content);
  } catch {
    console.log('No configuration file found. Creating a new one...');
    config = { borg: {}, backup: {} };
    await saveConfig(config);
  }
  return config;
}
