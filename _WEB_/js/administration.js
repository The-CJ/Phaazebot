function admin_logout() {
  var x = getCookie("admin_session");
  var r = {};
  r['admin_session'] = x;
  $.post("/api/admin/logout", JSON.stringify(r), function (data) {
    document.cookie = "admin_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC;"
    window.location = "/admin";
  })
}

function toggle_module(mo) {
  $.post("/api/admin/toggle_moduls?modul="+mo, function (data) {
  })
}

function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
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