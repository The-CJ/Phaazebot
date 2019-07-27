var DiscordDashboard = new (class {
  constructor() {}

  loadHome() {
    DynamicURL.set("location", false);
    this.showLocationWindow();
  }

  loadConfig() {
    DynamicURL.set("location", "configs");
    this.showLocationWindow("configs");

  }
  loadCommand() {
    DynamicURL.set("location", "commands");
    this.showLocationWindow("commands");

  }
  loadLevel() {
    DynamicURL.set("location", "levels");
    this.showLocationWindow("levels");

  }
  loadQuote() {
    DynamicURL.set("location", "quotes");
    this.showLocationWindow("quotes");

  }
  showLocationWindow(location_name) {
    if ( isEmpty(location_name) ) { location_name = "home"; }
    $("[location]").hide();
    $("[location="+location_name+"]").show();
  }
  restoreView() {
    var l = DynamicURL.get("location");
    this.showLocationWindow(l);
    if (l == "home") { this.loadHome(); }
    else if (l == "config") { this.loadConfig(); }
    else if (l == "command") { this.loadCommand(); }
    else if (l == "level") { this.loadLevel(); }
    else if (l == "quote") { this.loadQuote(); }
  }
})

$("document").ready(function () {
  DiscordDashboard.restoreView();
})
