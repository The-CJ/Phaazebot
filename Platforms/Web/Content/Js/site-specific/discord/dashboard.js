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
        Template.find(".function").text(command.name);
        Template.find(".require").text( translateRequire(command.require) );
        Template.find(".cost").text(command.cost);
        Template.find(".uses").text(command.uses);
        Template.find(".cooldown").text(command.cooldown);
        Template.attr("command-id", command.id);

        if (command.hidden) {
          Template.find(".function").addClass("hidden");
          Template.find(".function").attr("title", "This is a hidden command and can not be viewed via web, without permissions");
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

var Commands = new (class {
  constructor() {

  }
  createModal() {
    $("#command_create").modal("show");
  }
  create() {
    var r = {
      "guild_id": $("#guild_id").val(),
      "trigger": $("#command_create [name=trigger]").val(),
      "content": $("#command_create [name=content]").val(),
      "function": $("#command_create [name=function]").val(),
      "complex": $("#command_create [name=commandtype]").val() == "complex" ? true : false,
      "hidden": $("#command_create [name=hidden]").is(":checked"),
      "cooldown": $("#command_create [name=cooldown]").val(),
      "require": $("#command_create [name=require]").val(),
      "required_currency": $("#command_create [name=required_currency]").val()
    };
    $.post("/api/discord/commands/create", r)
    .done(function (data) {
      Display.showMessage({content: "Successfull created command: "+data.command, color:Display.color_success});
      $("#command_create").modal("hide");
      DiscordDashboard.loadCommand();
      // after successfull command, reset modal
      $("#command_create [clear-after-success]").val(null);
      $("#command_create [command-setting], #command_create [extra-command-setting]").hide();
    })
    .fail(function (data) {
      console.log(data);
      let msg = data.responseJSON ? data.responseJSON.msg : "unknown"
      Display.showMessage({content: msg, color:Display.color_critical});
    })

  }

  detail(HTMLCommandRow) {
    var guild_id = $("#guild_id").val();
    var command_id = $(HTMLCommandRow).attr("command-id");
    $.get("/api/discord/commands/get", {guild_id: guild_id, command_id:command_id, show_hidden: true})
    .done(function (data) {
      var command = data.result[0];
      var currency = command.cost == 1 ? $("#guild_currency").val() : $("#guild_currency_multi").val();
      $("#command_detail [name=trigger]").text(command.trigger);
      $("#command_detail [name=require]").text( translateRequire(command.require) );
      $("#command_detail [name=uses]").text( command.uses + " times" );
      $("#command_detail [name=cost]").text( command.cost + " " + currency );


      $("#command_detail").modal("show");
    })
    .fail(function (data) {
      Display.showMessage({content: "Could not load command detail...", color:Display.color_critical});
      console.log(data);
    })
  }

  loadCommands(HTMLSelect) {
    $("[command-setting]").hide();
    var command_type = $(HTMLSelect).val();
    if (command_type == "complex") { $("[command-setting=complex]").show(); return;}

    if (command_type == "simple") {

      $.get("/api/discord/commands/list")
      .done(function (data) {
        var Options = $("#command_create [name=function]").html("");
        Options.append( $("<option value=''>Choose a function...</option>") );
        for (var cmd of data.result) {
          let Opt = $("<option>");
          Opt.attr("value", cmd.function);
          Opt.text(cmd.name);
          Options.append(Opt);
        }
        $("[command-setting=simple]").show();
      })
      .fail(function (data) {
        Display.showMessage({content: "Could not load command list...", color:Display.color_critical});
        console.log(data);
      })

    }
  }

  loadCommandInfo(HTMLSelect) {
    $("[extra-command-setting], [extra-command-setting] [name=content]").hide();
    var function_ = $(HTMLSelect).val();
    if (isEmpty(function_)) {return;}

    $.get("/api/discord/commands/list", {function: function_})
    .done(function (data) {

      if (data.result.length == 0) {
        return Display.showMessage({content: "Could not find your selected command...", color:Display.color_critical});
      }

      var cmd = data.result[0];

      $("#command_create [extra-command-setting] [name=description]").text(cmd.description);
      $("#command_create [extra-command-setting] [name=details]").text(cmd.details);
      if (cmd.need_content) {
        $("#command_create [extra-command-setting] [name=content]").show();
      }

      $("#command_create [extra-command-setting]").show();
    })
    .fail(function (data) {
      Display.showMessage({content: "Could not load command details...", color:Display.color_critical});
      console.log(data);
    })
  }
})

// utils
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
