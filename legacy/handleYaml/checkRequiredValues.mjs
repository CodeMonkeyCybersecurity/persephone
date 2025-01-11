// Check if required values are set in the YAML config
async function checkYamlConfig(config) {
  const requiredValues = {
    'borg.repo': config?.borg?.repo,
    'borg.passphrase': config?.borg?.passphrase,
    'borg.encryption': config?.borg?.encryption,
    'backup.paths_to_backup': config?.backup?.paths_to_backup,
  };

  for (const [key, value] of Object.entries(requiredValues)) {
    if (!value) {
      config = await promptForMissingValue(config, key);
    }
  }
  await saveConfig(config);
  console.log('All required configuration values are set.');
  return true;
}
