// Restore a Borg archive
async function restoreBorgArchive(config, archiveName, targetDir) {
  const { repo, passphrase } = config.borg;
  process.env.BORG_PASSPHRASE = passphrase;

  try {
    await $`borg extract ${repo}::${archiveName} --target ${targetDir}`;
    console.log(`Restored archive '${archiveName}' to '${targetDir}'`);
  } catch (error) {
    console.error(`Restoring archive failed: ${error.stderr}`);
  }
}
