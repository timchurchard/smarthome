(function($){
  $(function(){

    var socket = new WebSocket("ws://10.0.1.23:8888/ws");

    socket.onmessage = function(msg) {
        console.log("socket.onmessage", msg);
    };


    $('.button-collapse').sideNav();


    $('#vol_up').on('click', function(evt) {
        socket.send('vol_up');
    });

    $('#vol_down').on('click', function(evt) {
        socket.send('vol_down');
    });

  }); // end of document ready
})(jQuery); // end of jQuery name space
