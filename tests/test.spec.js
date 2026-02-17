const { test, expect } = require('@playwright/test');
const { _electron: electron } = require('playwright');
const path = require('path');
const fs = require('fs');

let electronApp;
let window;

test.describe('Electron Application Tests', () => {

    test.beforeAll(async () => {
        electronApp = await electron.launch({
            args: [path.join(__dirname, '..', 'main.js')],
        });

        window = await electronApp.firstWindow();
        await window.waitForLoadState('domcontentloaded');
    });

    test.afterAll(async () => {
        await electronApp.close();
    });

    test('should launch application successfully', async () => {
        const title = await window.title();
        expect(title).toBe('sim');
    });

    test('should have correct window dimensions', async () => {
        const size = await window.evaluate(() => ({
          width: window.innerWidth,
          height: window.innerHeight
        }));

        expect(size.width).toBeGreaterThan(900);
        expect(size.height).toBeGreaterThan(800);
    });

    test('should display home section by default', async () => {
        const homeSection = await window.locator('#home');
        await expect(homeSection).toHaveClass(/active/);
    });

    test('should navigate to settings page', async () => {
        await window.click('a[href="#settings"]');

        const settingsSection = await window.locator('#settings');
        await expect(settingsSection).toHaveClass(/active/);
    });

    test('should have FAQ section', async () => {
        await window.click('a[href="#help"]');

        const helpSection = await window.locator('#help');
        await expect(helpSection).toHaveClass(/active/);

        const faqItems = await window.locator('.faq-item').count();
        expect(faqItems).toBeGreaterThan(0);
    });

    test('should expand FAQ items on click', async () => {
        await window.click('a[href="#help"]');

        const firstFaq = window.locator('.faq-item').first();
        await firstFaq.click();

        await expect(firstFaq).toHaveClass(/active/);
    });

    test('should have calibration sections', async () => {
        const relaxedSection = await window.locator('#relaxed_face');
        expect(relaxedSection).toBeTruthy();

        const distanceSection = await window.locator('#calibrate_distance');
        expect(distanceSection).toBeTruthy();
    });

    test('should navigate to calibration page', async () => {
        await window.click('a[href="#settings"]');
        await window.click('a[href="#relaxed_face"]');

        const calibrationSection = await window.locator('#relaxed_face');
        await expect(calibrationSection).toHaveClass(/active/);
    });

    test('should validate time inputs', async () => {
        await window.click('a[href="#settings"]');

        const nightLimitTime = await window.locator('#nightLimitTime');
        await nightLimitTime.fill('22:00');

        const value = await nightLimitTime.inputValue();
        expect(value).toBe('22:00');
    });

    test('should validate range inputs', async () => {
        await window.click('a[href="#settings"]');

        const blueLightDay = await window.locator('#blueLightFilterDay');
        await blueLightDay.fill('10');

        const value = await blueLightDay.inputValue();
        expect(parseInt(value)).toBe(10);
    });
});

    test.describe('Settings API Tests', () => {

    test.beforeAll(async () => {
        electronApp = await electron.launch({
            args: [path.join(__dirname, '..', 'main.js')],
        });
        window = await electronApp.firstWindow();
        await window.waitForLoadState('domcontentloaded');
    });

    test.afterAll(async () => {
        await electronApp.close();
    });

    test('should expose settingsAPI to window', async () => {
        const hasSettingsAPI = await window.evaluate(() => {
            return typeof window.settingsAPI !== 'undefined';
        });

        expect(hasSettingsAPI).toBe(true);
    });

    test('should expose fileAPI to window', async () => {
        const hasFileAPI = await window.evaluate(() => {
            return typeof window.fileAPI !== 'undefined';
        });

        expect(hasFileAPI).toBe(true);
    });

    test('settingsAPI should have required methods', async () => {
        const methods = await window.evaluate(() => {
            return {
                hasSave: typeof window.settingsAPI.saveSettings === 'function',
                hasLoad: typeof window.settingsAPI.loadSettings === 'function'
            };
        });

        expect(methods.hasSave).toBe(true);
        expect(methods.hasLoad).toBe(true);
    });
});

test.describe('Navigation Tests', () => {

    test.beforeAll(async () => {
        electronApp = await electron.launch({
            args: [path.join(__dirname, '..', 'main.js')],
        });
        window = await electronApp.firstWindow();
        await window.waitForLoadState('domcontentloaded');
    });

    test.afterAll(async () => {
        await electronApp.close();
    });

    test('should navigate through all main sections', async () => {
        const sections = ['#home', '#settings', '#help'];

        for (const section of sections) {
            await window.click(`a[href="${section}"]`);

            const activeSection = await window.locator(section);
            await expect(activeSection).toHaveClass(/active/);
        }
    });
});