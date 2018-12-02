$(document).ready(function() {
  //connect to the socket server.
  var socket = io.connect(
    "http://" + document.domain + ":" + location.port + "/market"
  )

  //receive details from server
  socket.on("leaderboard", function(msg) {
    data = JSON.parse(msg.data)

    var sell_price = data.orderbook.sell_price
    var old_sell_price = parseInt(
      $("#sell")
        .text()
        .replace(/,/g, "")
    )
    if (sell_price > old_sell_price)
      $("#sell_change").html("<font color='red'>BUY</font>")
    if (sell_price < old_sell_price)
      $("#sell_change").html("<font color='blue'>BUY</font>")
    if (sell_price == old_sell_price)
      $("#sell_change").html("<font color='black'>BUY</font>")
    $("#sell").text(sell_price.toLocaleString())

    var buy_price = data.orderbook.buy_price
    var old_buy_price = parseInt(
      $("#buy")
        .text()
        .replace(/,/g, "")
    )
    if (buy_price > old_buy_price)
      $("#buy_change").html("<font color='red'>SELL</font>")
    if (buy_price < old_buy_price)
      $("#buy_change").html("<font color='blue'>SELL</font>")
    if (buy_price == old_buy_price)
      $("#buy_change").html("<font color='black'>SELL</font>")
    $("#buy").text(buy_price.toLocaleString())
  })

  trade = function(decision, price) {
    var data = {
      agent_id: $("#agent_id").val(),
      decision: decision,
      price: price,
      quantity: parseFloat($("#quantity").val())
    }
    console.log(data)

    $.ajax({
      dataType: "json",
      url: "/api/m/trade",
      data: data,
      success: function(responseData) {
        for (var key in responseData) {
          if (key == "profit") $("#score").text(responseData[key])
        }
      }
    })
  }

  $("#sell_decision").click(function() {
    // sell
    trade(
      2,
      parseInt(
        $("#buy")
          .text()
          .replace(/,/g, "")
      )
    )
  })
  $("#buy_decision").click(function() {
    // buy
    trade(
      1,
      parseInt(
        $("#sell")
          .text()
          .replace(/,/g, "")
      )
    )
  })
})
