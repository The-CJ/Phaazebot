var DiscordDashboard = new (class {
  constructor() {}

  loadHome() {
    DynamicURL.set("view", false);
    this.showLocationWindow();
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/guild", {guild_id: guild_id})
    .done(function (data) {
      console.log(data);

      var guild = data.result;
      var image_link = "https://cdn.discordapp.com/icons/{guild_id}/{icon}.png?size=128";
      var image_alt = "https://cdn.discordapp.com/embed/avatars/{icon}.png";

      var image = "";

      if (guild.icon) {
        image = image_link;
        image = image.replace("{guild_id}", guild.id);
        image = image.replace("{icon}", guild.icon);
      } else {
        let r = guild.id % 5;
        image = image_alt;
        image = image.replace("{icon}", r);
      }
      $("#icon").attr("src", image);
      $("#name").text(guild.name);

      // stats
      $("#command_count").text(guild.command_count);
      $("#quote_count").text(guild.quote_count);
      $("#twitch_alert_count").text(guild.twitch_alert_count);
      $("#level_count").text(guild.level_count);

      // infos
      $("#member_count").text(guild.member_count);
      $("#role_count").text(guild.role_count);
      $("#channel_count").text(guild.channel_count);
      $("#premium_subscription_count").text(guild.premium_subscription_count ? guild.premium_subscription_count : 0);

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
    var guild_id = $("#guild_id").val();

    $.get("/api/discord/commands/get", {guild_id: guild_id, show_hidden: true})
    .done(function (data) {

      $("#command_amount").text(data.result.length);
      var CommandList = $("#command_list").html("");

      for (var command of data.result) {
        var Template = $("[phantom] .command").clone();
        Template.find(".trigger").text(command.trigger);
        Template.find(".content").text(command.content);
        Template.find(".require").text( translateRequire(command.require) );
        Template.find(".cost").text(command.cost);
        Template.find(".uses").text(command.uses);
        Template.attr("command-id", command.id);

        if (command.hidden) {
          Template.find(".content").addClass("hidden");
          Template.find(".content").attr("title", "Execute the command in the Discord server to see the result.");
        }

        CommandList.append(Template);
      }

    })
    .fail(function (data) {
      Display.showMessage({content: "Could not load commands...", color:Display.color_critical});
      console.log(data);
    })

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

function translateRequire(level) {
  if (level == 0) { return "Everyone"; }
  if (level == 1) { return "Regulars"; }
  if (level == 2) { return "Moderators"; }
  if (level == 3) { return "Server Owner"; }
  if (level >= 4) { return "System"; }
}

$("document").ready(function () {
  DiscordDashboard.restoreView();
})
