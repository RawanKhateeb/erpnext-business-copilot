import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright configuration for Copilot UI tests.
 * Uses POM (Page Object Model) pattern.
 */

const config = {
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: "http://localhost:8000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
    },
  ],
};

// Only add webServer for local development, not in CI
if (!process.env.CI) {
  config.webServer = {
    command: "cd ../.. && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000",
    url: "http://localhost:8000",
    reuseExistingServer: true,
    timeout: 120000,
  };
}

export default defineConfig(config);
