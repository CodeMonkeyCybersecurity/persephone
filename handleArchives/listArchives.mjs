// List all Borg archives
async function listBorgArchives(config) {
  const { repo, passphrase } = config.borg;
  process.env.BORG_PASSPHRASE = passphrase;

  try {
    await $`borg list ${repo}`;
  } catch (error) {
    console.error(`Listing archives failed: ${error.stderr}`);
  }
}
