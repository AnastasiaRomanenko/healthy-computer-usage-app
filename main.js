const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const featureProcesses = new Map();
let settingsWatcher = null;
let lastSettingsSnapshot = null;
const SETTINGS_PATH = path.join(__dirname, 'backend', 'assets', 'settings.json');

const FEATURE_MAP = {
    'eye_strain_prevention_enable': 'eye_strain_prevention',
    'distance_check_enable': 'distance_check',
    'night_limit_enable': 'night_limit',
    'daily_limit_enable': 'daily_limit',
    'break_reminders_enable': 'break_reminders',
    'blue_light_filter_enable': 'blue_light_filter'
};

const FEATURE_CONFIG_KEYS = {
    night_limit: ['night_limit_time'],
    daily_limit: ['daily_limit_time'],
    blue_light_filter: [
        'blue_light_filter_day',
        'blue_light_filter_evening',
        'blue_light_filter_night'
    ],
    distance_check: ['distance_check_area'],
    eye_strain_prevention: ['eye_strain_prevention_ratios']
};

function loadSettings() {
    try {
        if (fs.existsSync(SETTINGS_PATH)) {
            const data = fs.readFileSync(SETTINGS_PATH, 'utf8');
            return JSON.parse(data);
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
    return {};
}

function hasFeatureConfigChanged(featureName, oldSettings, newSettings) {
    const keys = FEATURE_CONFIG_KEYS[featureName];
    if (!keys) return false;

    return keys.some(key => oldSettings?.[key] !== newSettings?.[key]);
}

function startFeature(featureName) {
    if (featureProcesses.has(featureName)) {
        console.log(`Feature ${featureName} is already running`);
        return;
    }

    const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
    const scriptPath = path.join(__dirname, 'backend', 'features', `${featureName}.py`);

    if (!fs.existsSync(scriptPath)) {
        console.error(`Script not found: ${scriptPath}`);
        return;
    }

    console.log(`Starting feature: ${featureName}`);

    const pythonProcess = spawn(pythonPath,
        ['-m', `backend.features.${featureName}`],
        {
            cwd: __dirname
        }
    );

    pythonProcess.stdout.on('data', (data) => {
        console.log(`[${featureName}] ${data.toString().trim()}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`[${featureName} ERROR] ${data.toString().trim()}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`[${featureName}] Process exited with code ${code}`);
        featureProcesses.delete(featureName);
    });

    pythonProcess.on('error', (error) => {
        console.error(`[${featureName}] Failed to start:`, error);
        featureProcesses.delete(featureName);
    });

    featureProcesses.set(featureName, pythonProcess);
}

function stopFeature(featureName) {
    const process = featureProcesses.get(featureName);

    if (process) {
        console.log(`Stopping feature: ${featureName}`);
        process.kill('SIGTERM');
        featureProcesses.delete(featureName);
        if (featureName == "blue_light_filter") {
            const execSync = require('child_process').execSync;
            const output = execSync('nightlight off', { encoding: 'utf-8' });
        }
    }
}

function syncFeaturesWithSettings() {
    const settings = loadSettings();

    console.log('Syncing features with settings...');

    Object.entries(FEATURE_MAP).forEach(([settingKey, featureName]) => {
        const isEnabled = settings[settingKey] === true;
        const isRunning = featureProcesses.has(featureName);

        if (isEnabled && !isRunning) {
            console.log(`Enabling feature: ${featureName}`);
            startFeature(featureName);
        } else if (!isEnabled && isRunning) {
            console.log(`Disabling feature: ${featureName}`);
            stopFeature(featureName);
        }

        else if (isEnabled && isRunning &&
            hasFeatureConfigChanged(featureName, lastSettingsSnapshot, settings)) {
            console.log(`Reloading feature due to config change: ${featureName}`);
            stopFeature(featureName);

            setTimeout(() => {
                startFeature(featureName);
            } , 300);
        }
    });
    lastSettingsSnapshot = settings;
}

function watchSettingsFile() {
    if (settingsWatcher) {
        settingsWatcher.close();
    }

    if (!fs.existsSync(SETTINGS_PATH)) {
        const defaultSettings = {
            eye_strain_prevention_enable: false,
            distance_check_enable: false,
            night_limit_enable: false,
            night_limit_time: "22:00",
            daily_limit_enable: false,
            daily_limit_time: 4,
            break_reminders_enable: false,
            blue_light_filter_enable: false,
            blue_light_filter_day: 0,
            blue_light_filter_evening: 0,
            blue_light_filter_night: 80
        };

        const dir = path.dirname(SETTINGS_PATH);
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }

        fs.writeFileSync(SETTINGS_PATH, JSON.stringify(defaultSettings, null, 2));
    }

    console.log('Watching settings file for changes...');

    settingsWatcher = fs.watch(SETTINGS_PATH, (eventType) => {
        if (eventType === 'change') {
            console.log('Settings file changed, syncing features...');
            setTimeout(() => {
                syncFeaturesWithSettings();
            }, 500);
        }
    });
}

function stopAllProcesses() {
    console.log('Stopping all Python processes...');

    featureProcesses.forEach((process, name) => {
        console.log(`Stopping ${name}...`);
        process.kill('SIGTERM');

        if (name == "blue_light_filter") {
            const execSync = require('child_process').execSync;
            const output = execSync('nightlight off', { encoding: 'utf-8' });
        }
    });

    featureProcesses.clear();

    if (settingsWatcher) {
        settingsWatcher.close();
        settingsWatcher = null;
    }
}

const createWindow = () => {
    const win = new BrowserWindow({
        width: 1000,
        height: 850,
        webPreferences: {
          preload: path.join(__dirname, 'preload.js'),
          contextIsolation: true,
          nodeIntegration: false,
          webSecurity: false,
          sandbox: false
        }
    });

    win.loadFile('screens/index.html');

    win.webContents.on('will-navigate', (event, url) => {
        if (url.startsWith('file://')) return;
        event.preventDefault();
    });

    win.webContents.on('did-navigate', (event, url) => {
        console.log('Navigated to:', url);
    });
};

app.whenReady().then(() => {
    createWindow();
    lastSettingsSnapshot = loadSettings();
    watchSettingsFile();

    setTimeout(() => {
        syncFeaturesWithSettings();
    }, 1000);

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('before-quit', () => {
    stopAllProcesses();
});

app.on('window-all-closed', () => {
    stopAllProcesses();
    if (process.platform !== 'darwin') {
        app.quit();
    }
});