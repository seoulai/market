$(document).ready(function() {
  //connect to the socket server.
  var socket = io.connect(
    "http://" + document.domain + ":" + location.port + "/market"
  )
  var numbers_received = []

  //receive details from server
  socket.on("leaderboard", function(msg) {
    data = JSON.parse(msg.data)
    // console.log(data.rank)
    // console.log(data.orderbook)
    // console.log(data.prices)
    // TODO: update index.html
    //maintain a list of ten numbers
    // $('#log').html(numbers_string);
  })
})
