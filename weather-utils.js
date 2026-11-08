// weather-utils.js
const WEATHER_ICON_RULES = [
    { regex: /雷暴/, icon: "rain3_thunder.png" },
    { regex: /(短暫時間天晴|部分時間天晴|間中天晴|短暫天晴).*(幾陣雨|驟雨)|(幾陣雨|驟雨).*(短暫時間天晴|部分時間天晴)/, icon: "Sun_cloud_rain.png" },
    { regex: /幾陣驟雨|間中有驟雨|有驟雨|有幾陣雨|間中有雨|有雨|有微雨|有幾陣微雨/, icon: "rain2.png" },
    { regex: /煙霞|烟霞/, icon: "Haze.png" },
    { regex: /薄霧|薄雾/, icon: "fog1.png" },
    { regex: /霧|雾/, icon: "fog2.png" },
    { regex: /短暫時間天晴|部分時間天晴|間中天晴|短暫天晴|天晴，部分時間多雲/, icon: "Sun_cloud.png" },
    { regex: /天晴/, icon: "Sun.png" },
    { regex: /大致多雲|多雲|密雲|陰/, icon: "cloud.png" }
];

function getWeatherIcon(text) {
    if (!text) return 'cloud.png';
    for (const rule of WEATHER_ICON_RULES) {
        if (rule.regex.test(text)) {
            return rule.icon;
        }
    }
    return 'cloud.png';
}