// Prompt user for missing values
async function promptForMissingValue(config, key) {
  const question = `Please enter a value for ${key}: `;
  const value = await questionInput(question);
  const [category, field] = key.split('.');
  config[category][field] = value;
  return config;
}
