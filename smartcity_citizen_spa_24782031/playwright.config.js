const { defineConfig } = require('@playwright/test');

const baseURL = process.env.BASE_URL || 'http://103.151.63.84:8011';
const spaURL = process.env.SPA_URL || 'https://iet-polinela.github.io/project-2026-Syamsulhad1/';
const needsInsecureHttp = spaURL.startsWith('https://') && baseURL.startsWith('http://');

module.exports = defineConfig({
  testDir: './playwright',
  timeout: 30000,
  workers: 1,
  use: {
    browserName: 'chromium',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    launchOptions: {
      args: needsInsecureHttp
        ? ['--allow-running-insecure-content', '--disable-web-security']
        : [],
    },
  },
});
