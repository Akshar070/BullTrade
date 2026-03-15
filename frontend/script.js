// API BASE URL
const API = "https://bulltrade-api.onrender.com"

let priceChart
let volumeChart

let candleSeries
let volumeSeries

let currentStock = "RELIANCE.NS"


// Initialize charts
function initCharts() {

const container = document.getElementById("chart")

priceChart = LightweightCharts.createChart(container,{
width: container.clientWidth,
height: 400
})

volumeChart = LightweightCharts.createChart(
document.getElementById("volumeChart"),
{ height: 200 }
)

candleSeries = priceChart.addSeries(
LightweightCharts.CandlestickSeries
)

volumeSeries = volumeChart.addSeries(
LightweightCharts.HistogramSeries,
{ priceFormat:{ type:'volume' } }
)

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

candleSeries.setData(data)

const volumeData = data.map(d => ({
time: d.time,
value: d.volume,
color: d.close > d.open ? "#26a69a" : "#ef5350"
}))

volumeSeries.setData(volumeData)

})
.catch(err => console.error("Chart error:", err))

}


// Load selected stock
function loadStock(stock) {

currentStock = stock

document.getElementById("stockTitle").innerText = stock

fetch(`${API}/predict/${stock}`)
.then(res => res.json())
.then(data => {

if(data.error){
document.getElementById("prediction").innerHTML = "Prediction unavailable"
return
}

document.getElementById("prediction").innerHTML = `
<b>Current Price:</b> ₹${data.current_price}<br>
<b>Linear Regression Prediction:</b> ₹${data.lr_prediction}<br>
<b>Random Forest Prediction:</b> ₹${data.rf_prediction}<br>
<b>Prediction:</b> ${data.direction}
`

})
.catch(err => console.error("Prediction error:", err))

loadChart(stock,"1y")

}


// Timeframe buttons
function setTimeframe(range){
loadChart(currentStock, range)
}


// Search stock
function searchStock(){

const stock = document.getElementById("search").value.trim()

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
heatmap.innerHTML = ""

data.forEach(stock => {

const card = document.createElement("div")

card.className = "heatmap-card"

card.style.background =
stock.change > 0 ? "#0f9d58" : "#d93025"

card.innerHTML = `
${stock.stock}
<br>
${stock.percent.toFixed(2)}%
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