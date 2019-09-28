$("document").ready(async function () {
  DiscordDashboard.loadGeneralInfo();
  await sleep(250);
  DiscordDashboard.restoreView();
})

var DiscordDashboard = new (class {
  constructor() {
    this.channels = [];
    this.roles = [];
  }

  loadHome() {
    DynamicURL.set("view", false);
    this.showLocationWindow();
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/guild", {guild_id: guild_id})
    .done(function (data) {
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
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/get", {guild_id: guild_id})
    .done(function (data) {

      console.log(data.result);

      // insert current data
      insertData("[location=configs]", data.result);


    })
    .fail(function (data) {
      Display.showMessage({content: "Could not load configs...", color:Display.color_critical});
      console.log(data);
    })

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

  loadTwitchAlert() {
    DynamicURL.set("view", "twitch_alerts");
    this.showLocationWindow("twitch_alerts");
    alert("Load and Display 'Twitch Alert' Info");

  }

  loadAssignRole() {
    DynamicURL.set("view", "assign_roles");
    this.showLocationWindow("assign_roles");
    alert("Load and Display 'Assign Role' Info");

  }

  // utils
  loadGeneralInfo() {
    var DashO = this;
    var guild_id = $("#guild_id").val();
    // same api call as in loadHome, but why not
    $.get("/api/discord/guild", {guild_id: guild_id})
    .done(function (data) {

      DashO.channels = data.result.channels;
      DashO.roles = data.result.roles;

      DashO.buildDiscordChannel(data.result.channels);

    })
    .fail(function (data) {
      Display.showMessage({content: "Error loading general informations...", color:Display.color_critical});
      console.log(data);
    })
  }

  buildDiscordChannel(channel_list) {
    var HTMLSelectList = $("select[discord-channel]");
    for (var HTMLSelect of HTMLSelectList) {
      HTMLSelect = $(HTMLSelect).html("");

      var only_type = HTMLSelect.attr("discord-channel");
      if ( HTMLSelect.attr("discord-channel-none") )  {
        HTMLSelect.append("<option value=''>(None)</option>");
      }
      for (var channel of channel_list) {
        var name = channel.name;
        if (only_type) {
          if (only_type != channel.channel_type) { continue; }
          if (channel.channel_type == "text") { name = "#" + name;  }
        }

        var Option = $("<option>");
        Option.attr("value", channel.id);
        Option.text(name);
        HTMLSelect.append(Option);
      }
    }
  }

  // view utils
  showLocationWindow(view) {
    if ( isEmpty(view) ) { view = "home"; }
    $("[location]").hide();
    $("[location="+view+"]").show();
    this.toggleSitePanel("hide");
  }

  toggleSitePanel(state) {
    if (isEmpty(state)) {
      state = $(".site-panel").hasClass("show");
      state = state ? "hide" : "show";
    }
    if (state == "hide") {
      $(".site-panel").removeClass("show");
      $(".site-panel-btn").removeClass("show");
    }
    if (state == "show") {
      $(".site-panel").addClass("show");
      $(".site-panel-btn").addClass("show");
    }
  }

  restoreView() {
    var l = DynamicURL.get("view");
    this.showLocationWindow(l);
    if (l == "home" || !l) { this.loadHome(); }
    else if (l == "configs") { this.loadConfig(); }
    else if (l == "commands") { this.loadCommand(); }
    else if (l == "levels") { this.loadLevel(); }
    else if (l == "quotes") { this.loadQuote(); }
    else if (l == "twitch_alerts") { this.loadTwitchAlert(); }
    else if (l == "assign_roles") { this.loadAssignRole(); }
  }
})

var Commands = new (class {
  constructor() {

  }

  createModal() {
    $("#command_create [clear-after-success]").val("");
    $("#command_create [command-setting=simple]").hide();
    $("#command_create [extra-command-setting], #command_create [extra-command-setting] [name=content]").hide();
    $("#command_create .modal-title").text("New Command");
    $("#command_create").attr("mode", "new");
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
      $("#command_create [clear-after-success]").val("");
      $("#command_create [command-setting], #command_create [extra-command-setting]").hide();
    })
    .fail(function (data) {
      console.log(data);
      let msg = data.responseJSON ? data.responseJSON.msg : "unknown"
      Display.showMessage({content: msg, color:Display.color_critical});
    })

  }

  delete() {
    var r = {
      "guild_id": $("#guild_id").val(),
      "trigger": $("#command_create [name=trigger]").val(),
    };
    if (!confirm("Are you sure you want to delete the command?")) { return; }
    $.post("/api/discord/commands/delete", r)
    .done(function (data) {
      Display.showMessage({content: "Successfull deleted command: "+data.command, color:Display.color_success});
      $("#command_create").modal("hide");
      DiscordDashboard.loadCommand();
    })
    .fail(function (data) {
      console.log(data);
      let msg = data.responseJSON ? data.responseJSON.msg : "unknown"
      Display.showMessage({content: msg, color:Display.color_critical});
    })
  }

  edit() {
    var r = {
      "guild_id": $("#guild_id").val(),
      "command_id": $("#command_create [name=command_id]").val(),
      "trigger": $("#command_create [name=trigger]").val(),
      "content": $("#command_create [name=content]").val(),
      "function": $("#command_create [name=function]").val(),
      "complex": $("#command_create [name=commandtype]").val() == "complex" ? true : false,
      "hidden": $("#command_create [name=hidden]").is(":checked"),
      "cooldown": $("#command_create [name=cooldown]").val(),
      "require": $("#command_create [name=require]").val(),
      "required_currency": $("#command_create [name=required_currency]").val()
    };
    $.post("/api/discord/commands/edit", r)
    .done(function (data) {
      Display.showMessage({content: "Successfull edited command: "+data.command, color:Display.color_success});
      $("#command_create").modal("hide");
      DiscordDashboard.loadCommand();
    })
    .fail(function (data) {
      console.log(data);
      let msg = data.responseJSON ? data.responseJSON.msg : "unknown"
      Display.showMessage({content: msg, color:Display.color_critical});
    })
  }

  detail(HTMLCommandRow) {
    var CommandsObj = this;
    var guild_id = $("#guild_id").val();
    var command_id = $(HTMLCommandRow).attr("command-id");
    $.get("/api/discord/commands/get", {guild_id: guild_id, command_id:command_id, show_hidden: true})
    .done(function (data) {
      var command = data.result[0];

      $("#command_create .modal-title").text("Edit command: "+command.trigger);
      $("#command_create [name=command_id]").val(command.id);
      $("#command_create [name=trigger]").val(command.trigger);
      $("#command_create [name=require]").val( command.require );
      $("#command_create [name=required_currency]").val( command.cost );
      $("#command_create [name=uses]").val( command.uses );
      $("#command_create [name=cooldown], #command_create [name=cooldown_slider]").val( command.cooldown );
      $("#command_create [name=commandtype]").val( command.complex ? "complex" : "simple" );
      if (command.hidden) { $("#command_create [name=hidden]").prop( "checked", true ); }
      else { $("#command_create [name=hidden]").prop( "checked", false ); }

      if (!command.complex) {
        CommandsObj.loadCommands(null, "simple", command.function);
        CommandsObj.loadCommandInfo(null, command.function);
      }

      $("#command_create [extra-command-setting] [name=content]").val(command.content);
      $("#command_create").attr("mode", "edit");
      $("#command_create").modal("show");
    })
    .fail(function (data) {
      Display.showMessage({content: "Could not load command details...", color:Display.color_critical});
      console.log(data);
    })
  }

  loadCommands(HTMLSelect, command_type, preselected) {
    $("#command_create [command-setting]").hide();
    var command_type = $(HTMLSelect).val() || command_type;
    if (command_type == "complex") {
      $("[command-setting=complex]").show();
      return;
    }

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
        if (preselected) { Options.val(preselected); }
        $("[command-setting=simple]").show();
      })
      .fail(function (data) {
        Display.showMessage({content: "Could not load command list...", color:Display.color_critical});
        console.log(data);
      })

    }
  }

  loadCommandInfo(HTMLSelect, preselected) {
    $("#command_create [extra-command-setting], #command_create [extra-command-setting] [name=content]").hide();
    var function_ = $(HTMLSelect).val() || preselected;
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

var Configs = new(class {
  constructor() {

  }

  showWordBlacklist() {
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/get", {guild_id: guild_id})
    .done(function (data) {

      var EntryList = $("#config_modal_blacklist_words .wordbanlist").html("");
      for (var entry of data.result.blacklist_words) {
        var EntryRow = $("[phantom] .blacklistword").clone();
        EntryRow.find(".word").text(entry);
        EntryList.append(EntryRow);
      }
      $("#config_modal_blacklist_words").modal("show");
    })
    .fail(function (data) {
      let msg = data.responseJSON ? data.responseJSON.msg : "Error loading word blacklist..."
      Display.showMessage({content: msg, color:Display.color_critical});
      console.log(data);
    })
  }

  removeFromBlacklist(HTMLButton) {
    var Entry = $(HTMLButton).closest(".blacklistword");
    var word = Entry.find(".word").text();

    var req = {
      "blacklist_word": word,
      "blacklist_action": "remove"
    };
    this.update(req);
    Entry.remove();
  }

  updateField(HTMLForm) {
    var extracted_data = extractData($(HTMLForm));
    this.update(extracted_data);
  }

  updateToogleField(HTMLForm) {
    var extracted_data = extractData($(HTMLForm));
    var update_request = {};

    for (var key in extracted_data) {
      var value = extracted_data[key];
      var opposite_value = oppositeValue(value);
      update_request[key] = opposite_value;
    }

    this.update(update_request);
  }

  update(new_configs) {
    var guild_id = $("#guild_id").val();
    new_configs["guild_id"] = guild_id

    $.post("/api/discord/configs/edit", new_configs)
    .done(function (data) {

      insertData("[location=configs]", data.changes, true);
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});

    })
    .fail(function (data) {
      let msg = data.responseJSON ? data.responseJSON.msg : "Error updating configs..."
      Display.showMessage({content: msg, color:Display.color_critical});
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

function showTokenHelp(field) {
  if (isEmpty(field)) { field = ""; }
  else { field = "."+field; }
  $("#token_modal_help .token").hide();
  $("#token_modal_help .token"+field).show();
  $("#token_modal_help").modal("show");
}
