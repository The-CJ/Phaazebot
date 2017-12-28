function discord_logout() {
  var x = getCookie("discord_session");
  var r = {};
  r['discord_session'] = x;
  $.post("/api/discord/logout", JSON.stringify(r), function (data) {
    document.cookie = "discord_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC;"
    window.location = "/discord";
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

function load_discord_servers() {
  var x = getCookie("discord_session");
  var r = {};
  r['discord_session'] = x;
  $.post("/api/discord/get_servers", JSON.stringify(r), function (data) {
    for (var server in data) {
      if (data[server].owner == true) {
        var preset = $("#server_preset").html();
        preset = preset.replace(/\[serverid\]/g, data[server].id);
        preset = preset.replace(/\[icon\]/g, data[server].icon);
        preset = preset.replace(/\[server_name\]/g, escapeHtml(data[server].name));
        $('#your_servers').append(preset);
      } else if (data[server].manage == true) {
        var preset = $("#server_preset").html();
        preset = preset.replace(/\[serverid\]/g, data[server].id);
        preset = preset.replace(/\[icon\]/g, data[server].icon);
        preset = preset.replace(/\[server_name\]/g, escapeHtml(data[server].name));
        $('#manageble_servers').append(preset);
      } else {
        var preset = $("#server_preset").html();
        preset = preset.replace(/\[serverid\]/g, data[server].id);
        preset = preset.replace(/\[icon\]/g, data[server].icon);
        preset = preset.replace(/\[server_name\]/g, escapeHtml(data[server].name));
        $('#viewable_servers').append(preset);
      }
    }
    }
  )
}

$('document').ready(function(){
  load_discord_servers();
});

