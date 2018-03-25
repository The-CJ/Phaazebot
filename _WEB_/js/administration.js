function admin_logout() {
  var x = getCookie("phaaze_session");
  var r = {};
  r['phaaze_session'] = x;
  $.post("/api/logout", JSON.stringify(r), function (data) {
    remCookie("phaaze_session");
    window.location = "/admin";
  })
}

function toggle_module(mo) {
  $.post("/api/admin/toggle_moduls?modul="+mo, function (data) {
    _show_message('Successfull toggled', 'background:#44FF44;')
  })
  .fail(function (data) {
    _show_message('Unauthorized', 'background:white;');
  })

}

function evalCommand() {
  var command = $('#eval_command').val();
  var r = {};
  r['command'] = command;
  $.post("/api/admin/eval_command", JSON.stringify(r), function (data) {
    $('#result_data').html(data.result);
  })
    .fail(function (data) {
      _show_message('Unauthorized', 'background:white;');
    })

}

function change_name() {
  var r = {};
  r['name'] = $('#discord_bot_name').val();
  $.post("/api/discord/change_bot_name", JSON.stringify(r), function (data) {})
  .fail(function (data) {
    _show_message('Unauthorized', 'background:white;');
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
       fail: function (data) {_show_message('Unauthorized', 'background:white;')},

	   processData: false,
	   contentType: "application/octet-stream",
   });
 }
  reader.readAsArrayBuffer(r);
}

function update_source_file() {
  var text = $('#textarea_field').val();
  var name = $('#hidden_page_index').text();
  $.post("/api/admin/files/edit?file="+name, text, function (data) {
    _show_message('Successfull saved', 'background:#44FF44;')
  })
  .fail(function (data) {
    _show_message('Unauthorized', 'background:white;');
  })
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