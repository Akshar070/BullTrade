let priceChart
let volumeChart

let candleSeries
let volumeSeries

let currentStock = "RELIANCE.NS"


function initCharts(){

const container = document.getElementById("chart")

priceChart = LightweightCharts.createChart(container,{
width:container.clientWidth,
height:400
})

volumeChart = LightweightCharts.createChart(
document.getElementById("volumeChart"),
{height:200}
)

candleSeries = priceChart.addSeries(
LightweightCharts.CandlestickSeries
)

volumeSeries = volumeChart.addSeries(
LightweightCharts.HistogramSeries,
{priceFormat:{type:'volume'}}
)

}


function loadChart(stock,range){

fetch(`http://127.0.0.1:5000/history/${stock}/${range}`)
.then(res=>res.json())
.then(data=>{

if(!Array.isArray(data)) return

candleSeries.setData(data)

const volumeData=data.map(d=>({
time:d.time,
value:d.volume,
color:d.close>d.open?"#26a69a":"#ef5350"
}))

volumeSeries.setData(volumeData)

})

}


function loadStock(stock){

currentStock=stock

document.getElementById("stockTitle").innerText=stock

fetch(`http://127.0.0.1:5000/predict/${stock}`)
.then(res=>res.json())
.then(data=>{

document.getElementById("prediction").innerHTML=`

<b>Current Price:</b> ₹${data.current_price}<br>
<b>Linear Regression Prediction:</b> ₹${data.lr_prediction}<br>
<b>Random Forest Prediction:</b> ₹${data.rf_prediction}<br>
<b>Prediction:</b> ${data.direction}

`

})

loadChart(stock,"1y")

}


function setTimeframe(range){

loadChart(currentStock,range)

}


function searchStock(){

const stock=document.getElementById("search").value.trim()

if(stock===""){
alert("Enter stock symbol like TCS.NS")
return
}

loadStock(stock)

}


function loadMarket(){

fetch("http://127.0.0.1:5000/market")
.then(res=>res.json())
.then(data=>{

const list=document.getElementById("market")

list.innerHTML=""

data.forEach(stock=>{

const li=document.createElement("li")

li.innerHTML=`
${stock.stock} ₹${stock.price}
`

li.onclick=()=>loadStock(stock.stock)

list.appendChild(li)

})

})

}


function loadHeatmap(){

fetch("http://127.0.0.1:5000/market")
.then(res=>res.json())
.then(data=>{

const heatmap=document.getElementById("heatmap")

heatmap.innerHTML=""

data.forEach(stock=>{

const card=document.createElement("div")

card.className="heatmap-card"

card.style.background=
stock.change>0?"#0f9d58":"#d93025"

card.innerHTML=`
${stock.stock}
<br>
${stock.percent.toFixed(2)}%
`

card.onclick=()=>loadStock(stock.stock)

heatmap.appendChild(card)

})

})

}


window.onload=function(){

initCharts()

loadStock(currentStock)

loadMarket()

loadHeatmap()

}