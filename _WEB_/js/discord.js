function discord_logout() {
  var x = getCookie("discord_session");
  var r = {};
  r['discord_session'] = x;
  $.post("/api/discord/logout", JSON.stringify(r), function (data) {
    remCookie("discord_session");
    window.location = "/discord";
  })
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
