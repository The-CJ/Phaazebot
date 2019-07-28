var DiscordDashboard = new (class {
  constructor() {}

  loadHome() {
    DynamicURL.set("view", false);
    this.showLocationWindow();
    alert("Load and Display 'Home' Info");
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/guild", {guild_id: guild_id})
    .done(function (data) {
      console.log(data);
    })
    .fail(function (data) {
      console.log(data);
    })
  }

  loadConfig() {
    DynamicURL.set("view", "configs");
    this.showLocationWindow("configs");
    alert("Load and Display 'Command' Info");

  }
  loadCommand() {
    DynamicURL.set("view", "commands");
    this.showLocationWindow("commands");
    alert("Load and Display 'Command' Info");

  }
  loadLevel() {
    DynamicURL.set("view", "levels");
    this.showLocationWindow("levels");
    alert("Load and Display 'Level' Info");

  }
  loadQuote() {
    DynamicURL.set("view", "quotes");
    this.showLocationWindow("quotes");
    alert("Load and Display 'Quote' Info");

  }

  showLocationWindow(view) {
    if ( isEmpty(view) ) { view = "home"; }
    $("[location]").hide();
    $("[location="+view+"]").show();
  }
  restoreView() {
    var l = DynamicURL.get("view");
    this.showLocationWindow(l);
    if (l == "home" || !l) { this.loadHome(); }
    else if (l == "configs") { this.loadConfig(); }
    else if (l == "commands") { this.loadCommand(); }
    else if (l == "levels") { this.loadLevel(); }
    else if (l == "quotes") { this.loadQuote(); }
  }
})

$("document").ready(function () {
  DiscordDashboard.restoreView();
})
