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
  $.post("/api/discord/get_servers", function (data) {
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

function get_server_custom_commands(server_id) {
  $.get("/api/discord/get_server_custom_commands?id="+server_id, function (data) {
    $('#custom_command_content').text('');
    for (var command in data.data) {
      var clone = $('#custom_command_phantom').clone().html();
      var cmd = data.data[command];

      clone = clone.replace(/{custom_list_id}/g, command);

      clone = clone.replace('{trigger}', escapeHtml(cmd.trigger));
      clone = clone.replace('{content}', escapeHtml(cmd.text));
      clone = clone.replace('{uses}', escapeHtml(cmd.uses));

      $('#custom_command_content').append(clone);
      // data.data[command]

    }
  })
}

function delete_custom_command(server_id, trigger) {
  var r = {};
  r['server_id'] = server_id;
  r['trigger'] = trigger;
  $.post("/api/discord/delete_custom_command", JSON.stringify(r), function (data) {})
  get_server_custom_commands(server_id);
}

function update_custom_command(server_id, trigger, content) {
  alert(server_id +" - "+  trigger);
}