$('document').ready(function () {
  load_status();
})

function load_status() {

  $.get("/api/admin/status")
  .fail(function (data) {
    m = data.responseJSON ? data.responseJSON.msg : "unknown";
    _show_message(m, "red");
  })
  .done(function (data) {
    // version
    $("#version").text(data.result.version);

    // uptime
    let minutes = data.result.uptime / 60;
    let seconds = data.result.uptime % 60
    let hours = minutes / 60
    minutes = minutes % 60
    $("#uptime").text(parseInt(hours)+"h "+parseInt(minutes)+"m "+parseInt(seconds)+"s");

    // module status
    for (var mstat in data.result.module_status) {
      var b = $("#status_"+mstat);
      if (b == null) {continue}
      let cur_s = data.result.module_status[mstat];
      let name = mstat;
      let s = false;
      if (cur_s) {
        b.addClass("btn-success").removeClass("btn-danger");
        b.text("Active");
        s=false;
      } else {
        b.addClass("btn-danger").removeClass("btn-success");
        b.text("Inactive");
        s=true;
      }
      b.click(function () {
        $.post("/api/admin/controll", JSON.stringify({"action":"module", "module":name,"state":s})).done(location.reload())
      });
    }

    // Discord
    if (data.result.discord) {
      for (var variable in data.result.discord) {
        if (variable == "bot_avatar") {
          $("[name=discord_"+variable+"]").attr("src", data.result.discord[variable]);
          continue;
        }
        $("[name=discord_"+variable+"]").text(data.result.discord[variable]);
      }
    } else {
      let b = $("[name^=discord]").text("[N/A]");
      $("[name=discord_bot_avatar]").attr("src",null);
    }

    // Twitch
    if (data.result.twitch) {
      for (var variable in data.result.twitch) {
        $("[name=twitch_"+variable+"]").text(data.result.twitch[variable]);
      }
    } else {
      let b = $("[name^=twitch]").text("[N/A]");
    }


    console.log(data);
  })

}

function upload_avatar() {
  var f = $('#new_avatar');
  var u = {
    "action": "discord_avatar",
    "file": f[0].files[0],
  };
  var p = "/api/admin/controll";
  function s(data) {
    _hide_loading();
    _show_message(data.msg, "green");
  }
  function fa(data) {
    _hide_loading();
    _show_message(data.msg ? data.msg : "Critical Error", "red");
  }
  _show_loading("Uploading...");
  upload_file(u, p, s, fa);
}