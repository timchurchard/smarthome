(function($){
  $(function(){

    var socket = new WebSocket('ws://' + window.location.hostname + ':' + window.location.port + '/ws');
    var lamp_state = false;

    socket.onmessage = function(msg) {
        console.log("socket.onmessage", msg);
        try {
            var obj = JSON.parse(msg.data);
            if(obj.from == 'snd_ctrl') {
                $('#gaugeDemo .gauge-arrow').trigger('updateGauge', obj.level);
                $('#vol_level')[0].innerHTML = "Level: " + obj.level;
            }
            if(obj.from == 'lamp_ctrl') {
                var state = "Off";
                $('#liv_lamp_icon').css('color', '#a3a3c2');
                lamp_state = obj.state;
                if(obj.state) {
                    state = "On";
                    $('#liv_lamp_icon').css('color', '#ffff00');
                }
                $('#liv_lamp_text')[0].innerHTML = "(" + state + ")";
            }
            if(obj.from == 'temp') {
                $('#temp_live')[0].innerHTML = "Hallway: " + obj.temp + " C";
            }
            if(obj.from == 'loop') {
                $('#elec_live')[0].innerHTML = "Electricity: " + obj.usage + " kW";
            }
            if(obj.from == 'nest') {
                $('#nest_live')[0].innerHTML = "Nest: " + obj.data.temp + "/" + obj.data.target + " (" + obj.data.state + ")";
                if(obj.data.emergency) {
                    alert("Nest Emergency Flag Set WTF ??");
                }
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

    $('#liv_lamp').on('click', function(evt) {
        if(lamp_state) socket.send('lamp_off');
        else socket.send('lamp_on');
    });

  }); // end of document ready
})(jQuery); // end of jQuery name space
