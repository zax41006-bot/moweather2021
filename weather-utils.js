// weather-utils.js
const WEATHER_ICON_RULES = [
    // 🌟 優先顯示極端氣溫與特殊天氣圖標 (移到最頂部)
    { regex: /天氣極端嚴寒/, icon: "cold3.png" },
    { regex: /天氣嚴寒/, icon: "cold2.png" },
    { regex: /天氣寒冷/, icon: "cold1.png" },
    { regex: /天氣極端酷熱/, icon: "hot2.png" },
    { regex: /天氣酷熱/, icon: "hot1.png" },
    { regex: /氣溫略降|氣溫下降|氣溫顯著下降|氣溫大幅顯著下降/, icon: "temperature drop.png" },

    // 原有的一般天氣圖標
    { regex: /雷暴/, icon: "rain2.png" },
    { regex: /(短暫時間天晴|部分時間天晴|間中天晴|短暫天晴).*(微雨)|(微雨).*(短暫時間天晴|部分時間天晴)/, icon: "Sun_cloud_rain-a.png" },
    { regex: /(短暫時間天晴|部分時間天晴|間中天晴|短暫天晴).*(幾陣雨)|(幾陣雨).*(短暫時間天晴|部分時間天晴)/, icon: "Sun_cloud_rain-b.png" },
    { regex: /(短暫時間天晴|部分時間天晴|間中天晴|短暫天晴).*(驟雨)|(驟雨).*(短暫時間天晴|部分時間天晴)/, icon: "Sun_cloud_rain-c.png" },
    { regex: /有微雨|間中有微雨|有幾陣微雨/, icon: "rain1a.png" },
    { regex: /有幾陣雨|間中有雨|有雨/, icon: "rain1b.png" },
    { regex: /幾陣驟雨|間中有驟雨|有驟雨/, icon: "rain1c.png" },
    { regex: /大驟雨/, icon: "rain3.png" },
    { regex: /煙霞|烟霞/, icon: "Haze.png" },
    { regex: /薄霧|薄雾/, icon: "fog1.png" },
    { regex: /霧|雾/, icon: "fog2.png" },
    { regex: /短暫時間天晴|部分時間天晴|間中天晴|短暫天晴|天晴，部分時間多雲/, icon: "Sun_cloud.png" },
    { regex: /天晴/, icon: "Sun.png" },
    { regex: /大致多雲|多雲/, icon: "cloud1.png" },
    { regex: /密雲|陰/, icon: "cloud2.png" }
];

function getWeatherIcon(text) {
    if (!text) return 'cloud1.png';
    for (const rule of WEATHER_ICON_RULES) {
        if (rule.regex.test(text)) {
            return rule.icon;
        }
    }
    return 'cloud.png';
}