function toggle_module(mo) {
  $.post("/api/admin/toggle_moduls?modul="+mo, function (data) {
    _show_message('Successfull toggled', 'background:#44FF44;')
  })
  .fail(function (data) {
    _show_message('Unauthorized', 'red');
  })

}

function evalCommand(command) {
  if (command == null) {
    command = $('#eval_command').val();
  }
  var r = {};
  r['command'] = command;
  $.post("/api/admin/eval_command", r)
    .done(function (data) {
      $('#result_data').text(data.result);
    })
    .fail(function (data) {
      let m = data.responseJSON ? data.responseJSON.msg : "unknown"
      _show_message(m, 'red');
    })

}

function change_name() {
  var r = {};
  r['name'] = $('#discord_bot_name').val();
  $.post("/api/discord/change_bot_name", JSON.stringify(r), function (data) {})
  .fail(function (data) {
    _show_message('Unauthorized', 'red');
  })
}

function change_picture() {
  var r = document.getElementById('picture_upload').files[0];
  var reader = new FileReader();
  reader.onload = function (evt) {
    $.ajax({
       type: "POST",
       url: "/api/discord/change_bot_picture",
       data: evt.target.result,
       success: function (data) { console.debug(data); },
       fail: function (data) {_show_message('Unauthorized', 'red')},

	   processData: false,
	   contentType: "application/octet-stream",
   });
 }
  reader.readAsArrayBuffer(r);
}

function disableAPI() {
  var f = confirm('Please confirm, without API, 3rd Party programs, and major intern task cannot run properly');
  if (!f) {
    return
  }


  var time = $('#api_timeout').val();
  $.post("/api/admin/shutdown/api?time="+time, function (data) {
    _show_message('API Disabled', 'background:#44FF44;')
  })
  .fail(function (data) {
    _show_message('Unauthorized', 'background:white;');
  })
}

function disableWEB() {
  var f = confirm('Please confirm, disableling PhaaazeWeb closes all API endpoints end removedes all remote interfaces');
  if (!f) {
    return
  }


  var time = $('#web_timeout').val();
  $.post("/api/admin/shutdown/web?time="+time, function (data) {
    _show_message('WEB Disabled', 'background:#44FF44;')

  })
  .fail(function (data) {
    _show_message('Unauthorized', 'background:white;');
  })
}