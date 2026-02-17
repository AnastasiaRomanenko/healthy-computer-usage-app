const { contextBridge, ipcRenderer } = require('electron')
const fs = require('fs');
const path = require('path');
const settingsPath = path.join(__dirname, "backend/assets/settings.json");


contextBridge.exposeInMainWorld('versions', {
    node: () => process.versions.node,
    chrome: () => process.versions.chrome,
    electron: () => process.versions.electron
})

contextBridge.exposeInMainWorld('fileAPI', {
    saveImage: (base64Data, file_name) => {
        const filePath = path.join(__dirname, `${file_name}.png`);
        fs.writeFileSync(filePath, base64Data, 'base64');
        return filePath;
    }
});

contextBridge.exposeInMainWorld("settingsAPI", {
    saveSettings: (settings) => {
        fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 4));
        console.log("Settings saved to", settingsPath);
    },
    loadSettings: () => {
        if (fs.existsSync(settingsPath)) {
            return JSON.parse(fs.readFileSync(settingsPath, "utf-8"));
        } else {
            return {};
        }
    }
});