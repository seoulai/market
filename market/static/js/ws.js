$(document).ready(function() {
  //connect to the socket server.
  var socket = io.connect(
    "http://" + document.domain + ":" + location.port + "/market"
  )

  //receive details from server
  socket.on("leaderboard", function(msg) {
    data = JSON.parse(msg.data)
    rank_string = ""
    for (var i = 0; i < data.rank.length; i++) {
      rank_string =
        rank_string +
        "<tr><th scope='row'>" +
        i.toString() +
        "</th>" +
        "</th><td>" +
        data.rank[i].name +
        "</td><td>" +
        data.rank[i].profit +
        "</td></tr>"
    }
    drawBasic(data.prices)
    $("#rank").html(rank_string)
    var sell_price = data.orderbook.sell_price
    var old_sell_price = parseInt(
      $("#sell")
        .text()
        .replace(/,/g, "")
    )
    if (sell_price > old_sell_price)
      $("#sell_change").html("<font color='red'>SELL</font>")
    if (sell_price < old_sell_price)
      $("#sell_change").html("<font color='blue'>SELL</font>")
    if (sell_price == old_sell_price)
      $("#sell_change").html("<font color='black'>SELL</font>")
    $("#sell").text(sell_price.toLocaleString())

    var buy_price = data.orderbook.buy_price
    var old_buy_price = parseInt(
      $("#buy")
        .text()
        .replace(/,/g, "")
    )
    if (buy_price > old_buy_price)
      $("#buy_change").html("<font color='red'>BUY</font>")
    if (buy_price < old_buy_price)
      $("#buy_change").html("<font color='blue'>BUY</font>")
    if (buy_price == old_buy_price)
      $("#buy_change").html("<font color='black'>BUY</font>")
    $("#buy").text(buy_price.toLocaleString())
  })

  google.charts.load("current", { packages: ["corechart", "line"] })
  google.charts.setOnLoadCallback(drawBasic)

  function drawBasic(d) {
    // console.log(d)
    var data = new google.visualization.DataTable()
    data.addColumn("date", "Datetime")
    data.addColumn("number", "Price")
    if (d !== undefined) {
      nd = []
      for (var i = 0; i < d.length; i++) {
        nd.push([new Date(d[i][0]), parseInt(d[i][1])])
      }
      data.addRows(nd)
    } else {
      data.addRows([
        [new Date(2014, 0), 0],
        [new Date(2014, 1), 10],
        [new Date(2014, 2), 23],
        [new Date(2014, 3), 17],
        [new Date(2014, 4), 18],
        [new Date(2014, 5), 9]
      ])
    }
    var options = {
      hAxis: {
        title: "Datetime",
        format: "M/d hh:mm"
      },
      vAxis: {
        title: "Price"
      },
      height: 400,
      width: "100%",
      legend: { position: "bottom" }
    }

    var chart = new google.visualization.LineChart(
      document.getElementById("chart_div")
    )

    chart.draw(data, options)
  }
})
