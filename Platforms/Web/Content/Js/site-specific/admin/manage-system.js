function loadStatus() {
  $.get("/api/admin/status")
  .done(function (data) {
    $("#version").text(data.result.version);
    buildUptime(data.result.uptime);
    buildModules(data.result.modules);
    buildDiscord(data.result.discord);
  })
  .fail(function (data) {
    console.log(data);
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
    Field.find(".value").text(modules[m] ? "Enabled" : "Disabled");
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

$("document").ready(function () {
  loadStatus();
})
