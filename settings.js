const saveButton = document.getElementById("saveSettings");

saveButton.addEventListener("click", async (e) => {
    e.preventDefault();

    const settings = {
        eye_strain_prevention_enable: document.getElementById("eyeStrainPreventionEnable").checked,
        distance_check_enable: document.getElementById("distanceCheckEnable").checked,

        night_limit_enable: document.getElementById("nightLimitEnable").checked,
        night_limit_time: document.getElementById("nightLimitTime").value,

        daily_limit_enable: document.getElementById("dailyLimitEnable").checked,
        daily_limit_time: document.getElementById("dailyLimitTime").value,

        break_reminders_enable: document.getElementById("breakRemindersEnable").checked,

        blue_light_filter_enable: document.getElementById("blueLightFilterEnable").checked,
        blue_light_filter_day: Number(document.getElementById("blueLightFilterDay").value),
        blue_light_filter_evening: Number(document.getElementById("blueLightFilterEvening").value),
        blue_light_filter_night: Number(document.getElementById("blueLightFilterNight").value)
    };
    window.settingsAPI.saveSettings(settings);
    loadSettings();
});

function loadSettings() {
    const settings = window.settingsAPI.loadSettings();

    document.getElementById("eyeStrainPreventionEnable").checked = settings.eye_strain_prevention_enable || false;
    document.getElementById("distanceCheckEnable").checked = settings.distance_check_enable || false;

    document.getElementById("nightLimitEnable").checked = settings.night_limit_enable || false;
    document.getElementById("nightLimitTime").value = settings.night_limit_time || "22:00";

    document.getElementById("dailyLimitEnable").checked = settings.daily_limit_enable || false;
    document.getElementById("dailyLimitTime").value = settings.daily_limit_time || "04:00";

    document.getElementById("breakRemindersEnable").checked = settings.break_reminders_enable || false;

    document.getElementById("blueLightFilterEnable").checked = settings.blue_light_filter_enable || false;
    document.getElementById("blueLightFilterDay").value = settings.blue_light_filter_day || 0;
    document.getElementById("blueLightFilterEvening").value = settings.blue_light_filter_evening || 40;
    document.getElementById("blueLightFilterNight").value = settings.blue_light_filter_night || 80;
}
window.addEventListener("DOMContentLoaded", loadSettings);