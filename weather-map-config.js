// weather-map-config.js

// 1. 實時分佈的氣象要素
const MONITOR_LAYERS = [
    { id: 'temp_now', label: '現時氣溫', icon: 'fa-solid fa-temperature-half', file: 'temp_now.png' },
    { id: 'temp_max', label: '最高氣溫', icon: 'fa-solid fa-temperature-arrow-up', file: 'temp_max.png' },
    { id: 'temp_min', label: '最低氣溫', icon: 'fa-solid fa-temperature-arrow-down', file: 'temp_min.png' },
    { id: 'humidity', label: '相對濕度', icon: 'fa-solid fa-droplet', file: 'humidity.png' },
    { id: 'rain_h', label: '一小時降水', icon: 'fa-solid fa-cloud-showers-heavy', file: 'rain_h.png' },
    { id: 'rain_d', label: '今日累計降水', icon: 'fa-solid fa-cloud-rain', file: 'rain_d.png' },
    { id: 'wind_speed', label: '實時風速', icon: 'fa-solid fa-wind', file: 'wind_speed.png' },
    { id: 'gust_speed', label: '陣風風速', icon: 'fa-solid fa-tornado', file: 'gust_speed.png' },
    { id: 'wind_dir', label: '風向分佈', icon: 'fa-solid fa-compass', file: 'wind_dir.png' }
];

// 2. 歷史折線圖的監測站點
const HISTORY_STATIONS = [
    { label: '九澳', code: '九澳' }, { label: '外港碼頭', code: '外港碼頭' },
    { label: '大潭山', code: '大潭山' }, { label: '大炮臺', code: '大炮臺' },
    { label: '媽閣', code: '媽閣' }, { label: '東亞運大馬路', code: '東亞運大馬路' },
    { label: '澳門大學', code: '澳門大學' }, { label: '紀念孫中山公園', code: '紀念孫中山公園' },
    { label: '路環', code: '路環' }, { label: '黑沙環', code: '黑沙環' },
    { label: '友誼大橋北', code: '友誼大橋北' }, { label: '友誼大橋南', code: '友誼大橋南' },
    { label: '嘉樂庇總督大橋', code: '嘉樂庇總督大橋' }, { label: '澳門大橋北', code: '澳門大橋北' },
    { label: '澳門大橋南', code: '澳門大橋南' }, { label: '蓮花大橋', code: '蓮花大橋' },
    { label: '西灣大橋', code: '西灣大橋' }
];

// 3. 歷史折線圖的數據變數
const HISTORY_TYPES = [
    { label: '氣溫', code: 'temp' }, { label: '相對濕度', code: 'humidity' },
    { label: '雨量', code: 'rain' }, { label: '風速', code: 'wind_speed' }
];