const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
    testDir: './tests',
    timeout: 30000,
    fullyParallel: true,

    forbidOnly: !!process.env.CI,

    retries: process.env.CI ? 2 : 0,

    reporter: [
        ['html', { outputFolder: 'test-results/html' }],
        ['json', { outputFile: 'test-results/results.json' }],
        ['list']
    ],

    use: {
        baseURL: 'file://',

        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
    },

    projects: [{
        name: 'electron',
        use: {
            ...devices['Desktop Chrome'],
        },
    },],
});