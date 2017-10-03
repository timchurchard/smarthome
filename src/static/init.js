(function($){
  $(function(){

    var socket = new WebSocket('ws://' + window.location.hostname + ':' + window.location.port + '/ws');

    socket.onmessage = function(msg) {
        console.log("socket.onmessage", msg);
        try {
            var obj = JSON.parse(msg.data);
            if(obj.from == 'snd_ctrl') {
                $('#gaugeDemo .gauge-arrow').trigger('updateGauge', obj.level);
                $('#vol_level')[0].innerHTML = "Level: " + obj.level;
            }
            if(obj.from == 'temp') {
                $('#temp_live')[0].innerHTML = "Hallway temperature: " + obj.temp + " C";
            }
            if(obj.from == 'loop') {
                $('#elec_live')[0].innerHTML = "Electricity usage: " + obj.usage + " kW";
            }
        } catch(e) {
            // TODO
        }
    };

    $('#gaugeDemo .gauge-arrow').cmGauge();
    $('#gaugeDemo .gauge-arrow').trigger('updateGauge', 0);

    $('.button-collapse').sideNav();


    $('#vol_up').on('click', function(evt) {
        socket.send('vol_up');
    });

    $('#vol_down').on('click', function(evt) {
        socket.send('vol_down');
    });

  }); // end of document ready
})(jQuery); // end of jQuery name space
