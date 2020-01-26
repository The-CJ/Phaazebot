function loadStatus() {
  $.get("/api/admin/status")
  .done(function (data) {
    $("#version").text(data.result.version);
    buildUptime(data.result.uptime);
    buildModules(data.result.modules);
    buildDiscord(data.result.discord);
  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"loading status failed"} );
  })
}

function buildUptime(seconds) {
  // uptime
  let minutes = seconds / 60;
  let hours = minutes / 60
  seconds = seconds % 60
  minutes = minutes % 60
  $("#uptime").text(parseInt(hours)+"h "+parseInt(minutes)+"m "+parseInt(seconds)+"s");
}

function buildModules(modules) {
  var Target = $("[part=phaaze] [modules]");
  for (m in modules) {
    var Field = $("[phantom] > .module").clone();
    Field.find(".name").text(m);
    Field.find(".value").attr("active", modules[m] ? "true" : "false");
    Target.append(Field);
  }
}

function buildDiscord(discord) {
  for (var name in discord) {
    var Field = $("[part=discord] #" + name);
    if (name == "bot_avatar_url") {
      Field.attr("src", discord[name]);
    } else {
      Field.text(discord[name]);
    }
  }
}

function changeModuleState(HTMLButton) {
  var btn = $(HTMLButton);
  let state = (btn.attr("active") == "true") ? true : false;
  let name = btn.closest(".module").find(".name").text();

  // since we want to change the state, and the current state is a bool, we flip it
  var new_state = !state;

  let r = {
    module: name,
    state: new_state ? "1" : "",
  };

  $.post("/api/admin/module", r)
  .done(function (data) {
    btn.attr("active", new_state);
    Display.showMessage( {content: data.msg, color:Display.color_success} );
  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"changing status failed"} );
  })
}

$("document").ready(function () {
  loadStatus();
})
