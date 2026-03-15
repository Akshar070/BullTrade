// API BASE URL (Change to "http://127.0.0.1:5000" if testing locally)
const API = "https://bulltrade-api.onrender.com"

let priceChart
let volumeChart

let candleSeries
let volumeSeries

let currentStock = "RELIANCE.NS"

// Initialize charts
function initCharts() {
    const container = document.getElementById("chart")
    if (!container) return; // Safety check if element is missing

    priceChart = LightweightCharts.createChart(container, {
        width: container.clientWidth,
        height: 400
    })

    candleSeries = priceChart.addSeries(LightweightCharts.CandlestickSeries)

    const volContainer = document.getElementById("volumeChart")
    if (volContainer) {
        volumeChart = LightweightCharts.createChart(volContainer, { height: 200 })
        volumeSeries = volumeChart.addSeries(
            LightweightCharts.HistogramSeries,
            { priceFormat: { type: 'volume' } }
        )
    }
}

// Load chart data
function loadChart(stock, range) {
    fetch(`${API}/history/${stock}/${range}`)
    .then(res => res.json())
    .then(data => {
        if(!Array.isArray(data)) {
            console.log("Invalid chart data:", data)
            return
        }

        // 1. Translate Python capital letters to Lightweight Charts lowercase format
        const formattedCandles = data.map(d => ({
            time: d.Date || d.Datetime, // Fallback for intraday data
            open: d.Open,
            high: d.High,
            low: d.Low,
            close: d.Close
        }));

        candleSeries.setData(formattedCandles);

        // 2. Safely map volume data if the volume chart exists
        if (volumeSeries) {
            const volumeData = data.map(d => ({
                time: d.Date || d.Datetime,
                value: d.Volume,
                color: d.Close > d.Open ? "#26a69a" : "#ef5350"
            }));
            volumeSeries.setData(volumeData);
        }
    })
    .catch(err => console.error("Chart error:", err))
}

// Load selected stock
function loadStock(stock) {
    currentStock = stock

    const titleEl = document.getElementById("stockTitle");
    if (titleEl) titleEl.innerText = stock;

    fetch(`${API}/predict/${stock}`)
    .then(res => res.json())
    .then(data => {
        const predEl = document.getElementById("prediction");
        if (!predEl) return;

        if(data.error){
            predEl.innerHTML = "Prediction unavailable"
            return
        }

        predEl.innerHTML = `
            <b>Current Price:</b> ₹${data.current_price}<br>
            <b>Linear Regression Prediction:</b> ₹${data.lr_prediction}<br>
            <b>Random Forest Prediction:</b> ₹${data.rf_prediction}<br>
            <b>Prediction:</b> ${data.direction}
        `
    })
    .catch(err => console.error("Prediction error:", err))

    loadChart(stock, "1y")
}

// Timeframe buttons
function setTimeframe(range){
    loadChart(currentStock, range)
}

// Search stock
function searchStock(){
    const searchEl = document.getElementById("search");
    if (!searchEl) return;
    
    const stock = searchEl.value.trim()

    if(stock === ""){
        alert("Enter stock symbol like TCS.NS")
        return
    }

    loadStock(stock)
}

// Load market movers
function loadMarket(){
    fetch(`${API}/market`)
    .then(res => res.json())
    .then(data => {
        const list = document.getElementById("market")
        if (!list) return; // Safety check
        
        list.innerHTML = ""

        data.forEach(stock => {
            const li = document.createElement("li")
            li.innerHTML = `${stock.stock} ₹${stock.price}`
            li.onclick = () => loadStock(stock.stock)
            list.appendChild(li)
        })
    })
    .catch(err => console.error("Market error:", err))
}

// Load heatmap
function loadHeatmap(){
    fetch(`${API}/market`)
    .then(res => res.json())
    .then(data => {
        const heatmap = document.getElementById("heatmap")
        if (!heatmap) return; // Safety check
        
        heatmap.innerHTML = ""

        data.forEach(stock => {
            const card = document.createElement("div")
            card.className = "heatmap-card"
            card.style.background = stock.change > 0 ? "#0f9d58" : "#d93025"
            card.innerHTML = `
                ${stock.stock}
                <br>
                ${stock.percent}%
            `
            card.onclick = () => loadStock(stock.stock)
            heatmap.appendChild(card)
        })
    })
    .catch(err => console.error("Heatmap error:", err))
}

// Initialize dashboard
window.onload = function(){
    initCharts()
    loadStock(currentStock)
    loadMarket()
    loadHeatmap()
}