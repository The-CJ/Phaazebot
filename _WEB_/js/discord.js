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
      var preset = $("#server_preset").html();
      var image_link = "src=\"https://cdn.discordapp.com/icons/[serverid]/[icon].png\"";
      var alternative_link = "src=\"https://cdn.discordapp.com/embed/avatars/[modular_rest].png\"";

      if (data[server].icon == null) {
        modular_rest = data[server].id % 5;
        alternative_link = alternative_link.replace(/\[modular_rest\]/g, modular_rest);
        preset = preset.replace(/\[image_link\]/g, alternative_link);
      } else {
        image_link = image_link.replace(/\[icon\]/g, data[server].icon);
        image_link = image_link.replace(/\[serverid\]/g, data[server].id);
        preset = preset.replace(/\[image_link\]/g, image_link);
      }

      preset = preset.replace(/\[serverid\]/g, data[server].id);
      preset = preset.replace(/\[server_name\]/g, escapeHtml(data[server].name));

      if (data[server].owner == true) {
        $('#your_servers').append(preset);
      }
      else if (data[server].manage == true) {
        $('#manageble_servers').append(preset);
      }
      else {
        $('#viewable_servers').append(preset);
      }

    }
  })
}

function get_server_custom_commands(server_id) {
  $.get("/api/discord/get_server_custom_commands?id="+server_id, function (data) {
    $('#custom_command_content').text('');
    var amount = 0;
    for (var command in data.data) {
      var clone = $('#custom_command_phantom').clone().html();
      var cmd = data.data[command];

      clone = clone.replace(/{custom_list_id}/g, command);

      clone = clone.replace('{trigger}', escapeHtml(cmd.trigger));
      clone = clone.replace('{content}', escapeHtml(cmd.text));
      clone = clone.replace('{uses}', escapeHtml(cmd.uses));

      $('#custom_command_content').append(clone);
      amount = amount + 1;
    }
    $('#number_of_custom_cmd').text(amount);
  })
}

function delete_custom_command(server_id, trigger) {
  var r = {};
  r['server_id'] = server_id;
  r['trigger'] = trigger;
  $.post("/api/discord/delete_custom_command", JSON.stringify(r), function (data) {})
}

function update_custom_command(server_id, trigger, content) {
  alert(server_id +" - "+  trigger);
}