function admin_logout() {
  var x = getCookie("admin_session");
  var r = {};
  r['admin_session'] = x;
  $.post("/api/admin/logout", JSON.stringify(r), function (data) {
    remCookie("admin_session");
    window.location = "/admin";
  })
}

function toggle_module(mo) {
  $.post("/api/admin/toggle_moduls?modul="+mo, function (data) {
  })
}

function change_name() {
  var r = {};
  r['name'] = $('#discord_bot_name').val();
  $.post("/api/discord/change_bot_name", JSON.stringify(r), function (data) {})
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
	   processData: false,
	   contentType: "application/octet-stream",
   });
 }
  reader.readAsArrayBuffer(r);
}

function update_source_file() {
  var text = $('#textarea_field').val();
  var name = $('#hidden_page_index').text();
  $.post("/api/admin/edit_file_content?file="+name, text, function (data) {})

}

function disableAPI() {
  var f = confirm('Please confirm, without API, 3rd Party programs, and major intern task cannot run properly');
  if (!f) {
    return
  }


  var time = $('#api_timeout').val();
  $.post("/api/admin/shutdown_api?time="+time, function (data) {})
}

function disableWEB() {
  var f = confirm('Please confirm, disableling PhaaazeWeb closes all API endpoints end removed all removed remote interfaces');
  if (!f) {
    return
  }


  var time = $('#web_timeout').val();
  $.post("/api/admin/shutdown_web?time="+time, function (data) {})
}