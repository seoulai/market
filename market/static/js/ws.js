$(document).ready(function() {
  google.charts.load("current", { packages: ["corechart", "line"] })
  google.charts.setOnLoadCallback(drawBasic)

  function drawBasic(d) {
    var data = new google.visualization.DataTable()
    data.addColumn("date", "Datetime")
    data.addColumn("number", "Price")
    if (d !== undefined) {
      nd = []
      for (var i = 0; i < d.length; i++) {
        nd.push([new Date(d[i][0] * 1000), parseInt(d[i][1])])
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
        title: "Datetime"
      },
      vAxis: {
        title: "Price"
      }
    }

    var chart = new google.visualization.LineChart(
      document.getElementById("chart_div")
    )

    chart.draw(data, options)
  }

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
    $("#ask").text(data.orderbook.ask_price.toLocaleString())
    $("#bid").text(data.orderbook.bid_price.toLocaleString())
  })
})
