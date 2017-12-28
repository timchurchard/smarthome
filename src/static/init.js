(function($){
  $(function(){

    var socket = new WebSocket('ws://' + window.location.hostname + ':' + window.location.port + '/ws');
    var lamp_state = false;
    var lights_state = {};

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
            if(obj.from == "lights_ctrl") {
                for(var idx in obj.data) {
                    console.log("Got light", idx, "state", obj.data[idx].state);
                    $("#" + idx + "_icon").css('color', obj.data[idx].state.on ? '#ffff00' : '#a3a3c2');
                    $("#" + idx + "_text")[0].innerHTML = "(" + (obj.data[idx].state.on ? "On" : "Off") + ")";
                    lights_state[idx] = obj.data[idx].state.on;
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

    $('#front_lamp').on('click', function(evt) {
        if(lights_state['front_lamp']) socket.send('front_lamp_off');
        else socket.send('front_lamp_on');
    });

    $('#kitchen_lamp').on('click', function(evt) {
        if(lights_state['kitchen_lamp']) socket.send('kitchen_lamp_off');
        else socket.send('kitchen_lamp_on');
    });

    $('#liv_lamp').on('click', function(evt) {
        if(lamp_state) socket.send('lamp_off');
        else socket.send('lamp_on');
    });

    $('#liv_main').on('click', function(evt) {
        if(lights_state['liv_main']) socket.send('liv_main_off');
        else socket.send('liv_main_on');
    });

    $('#upstairs_lamp').on('click', function(evt) {
        if(lights_state['upstairs_lamp']) socket.send('upstairs_lamp_off');
        else socket.send('upstairs_lamp_on');
    });

    $('#bedroom_lamp').on('click', function(evt) {
        if(lights_state['bedroom_lamp']) socket.send('bedroom_lamp_off');
        else socket.send('bedroom_lamp_on');
    });

  }); // end of document ready
})(jQuery); // end of jQuery name space
