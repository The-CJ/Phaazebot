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
    Configs.show();
  }

  loadCommand() {
    DynamicURL.set("view", "commands");
    this.showLocationWindow("commands");
    Commands.show();
  }

  loadLevel() {
    DynamicURL.set("view", "levels");
    this.showLocationWindow("levels");
    Levels.show();
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

      DashO.buildDiscordChannelSelect({"channel_list":DashO.channels});
      DashO.buildDiscordRolesSelect({"role_list":DashO.roles})

    })
    .fail(function (data) {
      Display.showMessage({content: "Error loading general informations...", color:Display.color_critical});
      console.log(data);
    })
  }

  buildDiscordChannelSelect(x) {
    // fill a select HTML Object with discord channels.
    // the setting can be taken from the html element or from the function call
    // function call is dominant

    // used field in object x
    // x["channel_list"] :: a list of `channel objects` {"id":"123456", "name":"something", "channel_type":"text"}
    // x["target"] :: a list of jquery select elements, or a string for a jquery search   [Default: "select[discord-channel]"]
    // x["include_none"] :: bool, if true, include a <option value=''>(None)</option> at first [Default: false]
    //   also true if Select HTML element has attribute: discord-channel-none=true
    // x["only_type"] :: string, if not emtpy, only list the matching types [Default: ""]
    //   also set by using the attribute: discord-channel=text   or   discord-channel=voice

    var HTMLSelectList = null;

    var channel_list = x["channel_list"]; if (isEmpty(channel_list)) {throw "empty channel_list";}
    var include_none = x["include_none"];
    var only_type = x["only_type"];
    var target = x["target"];
    if (target == undefined) { HTMLSelectList = $("select[discord-channel]"); }
    else if (typeof target == "string") { HTMLSelectList = $(target); }
    if (isEmpty(HTMLSelectList)) { throw "no targets"; }

    for (var HTMLSelect of HTMLSelectList) {
      // clear first
      HTMLSelect = $(HTMLSelect).html("");

      // per element vars
      var element_only_type = only_type == undefined ? HTMLSelect.attr("discord-channel") : only_type;
      var element_include_none = include_none == undefined ? HTMLSelect.attr("discord-channel-none") : include_none;

      // include a none?
      if ( element_include_none ) { HTMLSelect.append("<option value=''>(None)</option>"); }

      for (var channel of channel_list) {
        // make copy of name, since we keep the channellist untouched
        var name = channel.name;
        var id = channel.id;

        // only type?
        if (element_only_type) {
          if (element_only_type != channel.channel_type) { continue; }
        }

        // special format
        if (channel.channel_type == "text") { name = "#" + name;  }

        var Option = $("<option>");
        Option.text(name);
        Option.attr("value", id);
        HTMLSelect.append(Option);
      }
    }
  }

  buildDiscordRolesSelect(x) {
    // fill a select HTML Object with discord roles.
    // the setting can be taken from the html element or from the function call
    // function call is dominant

    // used field in object x
    // x["role_list"] :: a list of `role objects` {"id":"123456", "name":"something", "managed":false}
    // x["target"] :: a list of jquery select elements, or a string for a jquery search   [Default: "select[discord-role]"]
    // x["include_none"] :: bool, if true, include a <option value=''>(None)</option> at first [Default: false]
    //   also true if Select HTML element has attribute: discord-role-none=true
    // x["show_managed"] :: bool, if true, include managed roles in the select [Default: false]
    //   also true if Select HTML element has attribute: discord-role-managed=true

    var HTMLSelectList = null;

    var role_list = x["role_list"]; if (isEmpty(role_list)) {throw "empty role_list";}
    var include_none = x["include_none"];
    var show_managed = x["show_managed"];
    var target = x["target"];
    if (target == undefined) { HTMLSelectList = $("select[discord-role]"); }
    else if (typeof target == "string") { HTMLSelectList = $(target); }
    if (isEmpty(HTMLSelectList)) { throw "no targets"; }

    for (var HTMLSelect of HTMLSelectList) {
      // clear first
      HTMLSelect = $(HTMLSelect).html("");

      // per element vars
      var element_show_managed = show_managed == undefined ? HTMLSelect.attr("discord-role-managed") : show_managed;
      var element_include_none = include_none == undefined ? HTMLSelect.attr("discord-role-none") : include_none;

      // include a none?
      if ( element_include_none ) { HTMLSelect.append("<option value=''>(None)</option>"); }

      for (var role of role_list) {
        // make copy of name, since we keep the rolelist untouched
        var name = role.name;
        var id = role.id;

        // managed role?
        if (!element_show_managed && role.managed) { continue; }

        var Option = $("<option>");
        Option.text(name);
        Option.attr("value", id);
        HTMLSelect.append(Option);
      }
    }
  }

  getDiscordChannelByID(id) {
    for (var channel of this.channels) {
      if (channel.id == id) { return channel; }
    }
    return null;
  }

  getDiscordRoleByID(id) {
    for (var role of this.roles) {
      if (role.id == id) { return role; }
    }
    return null;
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

  show() {
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

  createModal() {
    $("#command_create [clear-after-success]").val("");
    $("#command_create [command-setting=simple]").hide();
    $("#command_create [extra-command-setting], #command_create [extra-command-setting] [name=content]").hide();
    $("#command_create .modal-title").text("New Command");
    $("#command_create").attr("mode", "new");
    $("#command_create").modal("show");
  }

  create() {
    var CommandsObj = this;
    var guild_id = $("#guild_id").val();
    var r = {
      "guild_id": guild_id,
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
      CommandsObj.show();
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
    var CommandsObj = this;
    var guild_id = $("#guild_id").val();
    var r = {
      "guild_id": guild_id,
      "trigger": $("#command_create [name=trigger]").val(),
    };

    if (!confirm("Are you sure you want to delete the command?")) { return; }

    $.post("/api/discord/commands/delete", r)
    .done(function (data) {
      Display.showMessage({content: "Successfull deleted command: "+data.command, color:Display.color_success});
      $("#command_create").modal("hide");
      CommandsObj.show();
    })
    .fail(function (data) {
      console.log(data);
      let msg = data.responseJSON ? data.responseJSON.msg : "unknown"
      Display.showMessage({content: msg, color:Display.color_critical});
    })
  }

  edit() {
    var CommandsObj = this;
    var guild_id = $("#guild_id").val();
    var r = {
      "guild_id": guild_id,
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
      CommandsObj.show();
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
    this.blacklist = [];
    this.whitelist = [];
    this.except_roleslist = [];
  }

  show() {
    var guild_id = $("#guild_id").val();

    $.get("/api/discord/configs/get", {guild_id: guild_id})
    .done(function (data) {

      // insert current data
      insertData("[location=configs]", data.result);

    })
    .fail(function (data) {
      Display.showMessage({content: "Could not load configs...", color:Display.color_critical});
      console.log(data);
    })
  }

  // links
  showLinkWhitelist() {
    var ConfigsO = this;
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/get", {guild_id: guild_id})
    .done(function (data) {
      ConfigsO.whitelist = data.result.blacklist_whitelistlinks;
      ConfigsO.buildLinkWhitelist(ConfigsO.whitelist);
      $("#config_modal_whitelist_links").modal("show");
    })
    .fail(function (data) {
      let msg = data.responseJSON ? data.responseJSON.msg : "Error loading word link whitelist..."
      Display.showMessage({content: msg, color:Display.color_critical});
      console.log(data);
    })
  }

  buildLinkWhitelist(whitelist_links) {
    var EntryList = $("#config_modal_whitelist_links .linkwhitelist").html("");
    for (var entry of whitelist_links) {
      var EntryRow = $("[phantom] .whitelistlink").clone();
      EntryRow.find(".link").text(entry);
      EntryList.append(EntryRow);
    }
  }

  addToLinkWhitelist() {
    var new_link = $("#new_whitelistlink").val();
    if (isEmpty(new_link)) { return; }
    var req = {
      "linkwhitelist_link": new_link,
      "linkwhitelist_action": "add"
    };
    var ConfigsO = this;
    var successfunc = function () {
      $("#new_whitelistlink").val("");
      ConfigsO.whitelist.push(new_link.toLowerCase());
      ConfigsO.buildLinkWhitelist(ConfigsO.whitelist);
    }
    var failfunc = function() {
      $("#new_whitelistlink").val("");
    }

    this.update(req, successfunc, failfunc);
  }

  removeFromLinkWhitelist(HTMLButton) {
    var Entry = $(HTMLButton).closest(".whitelistlink");
    var link = Entry.find(".link").text();

    var req = {
      "linkwhitelist_link": link,
      "linkwhitelist_action": "remove"
    };
    var ConfigsO = this;
    this.update(req, function () {
      var i = ConfigsO.whitelist.indexOf(link);
      ConfigsO.whitelist.splice(i, 1);
      ConfigsO.buildLinkWhitelist(ConfigsO.whitelist);
    });

  }

  // blacklist
  showWordBlacklist() {
    var ConfigsO = this;
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/get", {guild_id: guild_id})
    .done(function (data) {
      ConfigsO.blacklist = data.result.blacklist_blacklistwords;
      ConfigsO.buildWordBlacklist(ConfigsO.blacklist);
      $("#config_modal_blacklist_words").modal("show");
    })
    .fail(function (data) {
      let msg = data.responseJSON ? data.responseJSON.msg : "Error loading word blacklist..."
      Display.showMessage({content: msg, color:Display.color_critical});
      console.log(data);
    })
  }

  buildWordBlacklist(blacklist_blacklistwords) {
    var EntryList = $("#config_modal_blacklist_words .wordbanlist").html("");
    for (var entry of blacklist_blacklistwords) {
      var EntryRow = $("[phantom] .blacklistword").clone();
      EntryRow.find(".word").text(entry);
      EntryList.append(EntryRow);
    }
  }

  addToBlacklist() {
    var new_word = $("#new_blacklistword").val();
    if (isEmpty(new_word)) { return; }
    var req = {
      "wordblacklist_word": new_word,
      "wordblacklist_action": "add"
    };
    var ConfigsO = this;
    var successfunc = function() {
      $("#new_blacklistword").val("");
      ConfigsO.blacklist.push(new_word.toLowerCase());
      ConfigsO.buildWordBlacklist(ConfigsO.blacklist);
    }
    var failfunc = function () {
      $("#new_blacklistword").val("");
    }

    this.update(req, successfunc, failfunc);
  }

  removeFromBlacklist(HTMLButton) {
    var Entry = $(HTMLButton).closest(".blacklistword");
    var word = Entry.find(".word").text();

    var req = {
      "wordblacklist_word": word,
      "wordblacklist_action": "remove"
    };
    var ConfigsO = this;
    this.update(req, function () {
      var i = ConfigsO.blacklist.indexOf(word);
      ConfigsO.blacklist.splice(i, 1);
      ConfigsO.buildWordBlacklist(ConfigsO.blacklist);
    });
  }

  // roles
  showExecptionRoles() {
    var ConfigsO = this;
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/get", {guild_id: guild_id})
    .done(function (data) {
      ConfigsO.except_roleslist = data.result.blacklist_whitelistroles;
      ConfigsO.buildExecptionRoles(ConfigsO.except_roleslist);
      $("#config_modal_exeption_roles").modal("show");
    })
    .fail(function (data) {
      let msg = data.responseJSON ? data.responseJSON.msg : "Error loading execption roles..."
      Display.showMessage({content: msg, color:Display.color_critical});
      console.log(data);
    })
  }

  buildExecptionRoles(exceptionroles_roles) {
    var EntryList = $("#config_modal_exeption_roles .exceptionrolelist").html("");
    for (var entry of exceptionroles_roles) {
      var EntryRow = $("[phantom] .exceptionrole").clone();
      var role = DiscordDashboard.getDiscordRoleByID(entry);
      EntryRow.find("[role-id]").val(entry);
      EntryRow.find(".name").text( role ? role.name : "(DELETED ROLE)" );
      if (isEmpty(role)) {
        EntryRow.addClass("deleted");
        EntryRow.attr("title", "This role is deleted on the server and can be deleted here as well without any worries");
      }

      EntryList.append(EntryRow);
    }
  }

  addToExecptionRoles() {
    var new_role_id = $("#new_exceptionrole").val();
    if (isEmpty(new_role_id)) { return; }
    var req = {
      "exceptionrole_id": new_role_id,
      "exceptionrole_action": "add"
    };
    var ConfigsO = this;
    var successfunc = function() {
      $("#new_exceptionrole").val("");
      ConfigsO.except_roleslist.push(new_role_id.toLowerCase());
      ConfigsO.buildExecptionRoles(ConfigsO.except_roleslist);
    }
    var failfunc = function () {
      $("#new_exceptionrole").val("");
    }

    this.update(req, successfunc, failfunc);
  }

  removeFromExecptionRoles(HTMLButton) {
    var Entry = $(HTMLButton).closest(".exceptionrole");
    var role_id = Entry.find("[role-id]").val();

    var req = {
      "exceptionrole_id": role_id,
      "exceptionrole_action": "remove"
    };
    var ConfigsO = this;
    this.update(req, function () {
      var i = ConfigsO.except_roleslist.indexOf(role_id);
      ConfigsO.except_roleslist.splice(i, 1);
      ConfigsO.buildExecptionRoles(ConfigsO.except_roleslist);
    });
  }

  // update utils
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

  update(new_configs, success_function, fail_function) {
    var guild_id = $("#guild_id").val();
    new_configs["guild_id"] = guild_id;

    $.post("/api/discord/configs/edit", new_configs)
    .done(function (data) {

      insertData("[location=configs]", data.changes, true);
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});

      if (success_function) { success_function.call() }

    })
    .fail(function (data) {
      let msg = data.responseJSON ? data.responseJSON.msg : "Error updating configs..."
      Display.showMessage({content: msg, color:Display.color_critical});
      console.log(data);
      if (fail_function) { fail_function.call() }
    })
  }

})

var Levels = new(class {
  constructor() {
    this.results_per_page = 50;
    this.offset = 0;
    this.total = 0;
  }

  show(x={}) {
    var LevelO = this;
    var guild_id = $("#guild_id").val();
    var offset = x["offset"] ? x["offset"] : 0;

    $.get("/api/discord/levels/get", {guild_id: guild_id, detailed:true, offset:offset, limit:this.results_per_page})
    .done(function (data) {

      // store a copy of the current number of entrys
      LevelO.total = data.total;
      LevelO.offset = data.offset;
      LevelO.updatePageIndexButtons();

      var LevelList = $("#level_list").html("");

      for (var level of data.result) {
        var Template = $("[phantom] .level").clone();
        var avatar = discordAvatar(level.member_id, level.avatar);

        Template.find(".rank").text(level.rank);
        Template.find(".lvl").text(level.level);
        Template.find(".exp").text(level.exp);
        Template.find(".name").text( level.username );
        Template.find(".avatar").attr("src", avatar);
        Template.find(".medals").text(level.medals.length);
        Template.attr("member-id", level.member_id);

        if (level.edited) {
          Template.find(".exp").addClass("edited");
          Template.find(".exp").attr("title", "This member got edited, the stats can be wrong");
        }

        LevelList.append(Template);
      }

    })
    .fail(function (data) {
      Display.showMessage({content: "Could not load levels...", color:Display.color_critical});
      console.log(data);
    })
  }

  prevPage(first) {
    if (first) {
      this.offset = 0;
    } else {
      this.offset -= (this.results_per_page);
    }
    this.show({offset:this.offset});
  }

  nextPage(last) {
    if (last) {
      this.offset = parseInt(this.total / this.results_per_page) * this.results_per_page;
    } else {
      this.offset += (this.results_per_page);
    }
    this.show({offset:this.offset});
  }

  updatePageIndexButtons() {
    var current_page = (this.offset / this.results_per_page) + 1;
    var max_pages = parseInt((this.total / this.results_per_page) + 1)

    $("#level_pages .index").text(current_page);

    // no more prev pages
    if (current_page <= 1) {
      $("#level_pages .prev").attr("disabled", true);
    } else {
      $("#level_pages .prev").attr("disabled", false);
    }

    // no more next pages
    if (current_page >= max_pages) {
      $("#level_pages .next").attr("disabled", true);
    } else {
      $("#level_pages .next").attr("disabled", false);
    }

  }

  detail(HTMLCommandRow) {
    var LevelObj = this;
    var guild_id = $("#guild_id").val();
    var member_id = $(HTMLCommandRow).attr("member-id");
    $.get("/api/discord/levels/get", {guild_id: guild_id, member_id:member_id, detailed: true})
    .done(function (data) {
      var level = data.result[0];

      console.log(level);

      // set avatar
      var avatar = discordAvatar(level.member_id, level.avatar, 128);
      $("#level_modal_edit img").attr("src", avatar);

      // insert medals
      var EntryList = $("#level_modal_edit .medallist").html("");
      for (var entry of level.medals) {
        var EntryRow = $("[phantom] .medal").clone();
        EntryRow.find(".name").text( entry );
        EntryList.append(EntryRow);
      }

      // edited?
      $("#level_modal_edit [name=exp]").attr("edited", level.edited ? "true" : "false");

      insertData("#level_modal_edit", level);

      $("#level_modal_edit").attr("edit-member", level.member_id);
      $("#level_modal_edit").modal("show");

    })
    .fail(function (data) {
      Display.showMessage({content: "Could not load level details...", color:Display.color_critical});
      console.log(data);
    })
  }

  editExp() {
    var c = confirm("Editing the exp will leave a permanent [EDITED] mark, unless resettet to 0, be carefull. Want to continue?");
    if (!c) { return; }

    var new_exp = $("#level_modal_edit [name=exp]").val();
    this.update( {exp: new_exp} );
  }

  addMedal() {
    var new_medal = $("#new_medal").val();
    if (isEmpty(new_medal)) { return; }

    this.update();
  }

  update(level_update, success_function, fail_function) {
    var guild_id = $("#guild_id").val();
    level_update["guild_id"] = guild_id;
    var member_id = $("#level_modal_edit").attr("edit-member");
    level_update["member_id"] = member_id;

    $.post("/api/discord/levels/edit", level_update)
    .done(function (data) {

      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});

      if (success_function) { success_function.call() }

    })
    .fail(function (data) {
      let msg = data.responseJSON ? data.responseJSON.msg : "Error updating levels..."
      Display.showMessage({content: msg, color:Display.color_critical});
      console.log(data);
      if (fail_function) { fail_function.call() }
    })
  }

});

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

function discordAvatar(member_id, avatar_hash, size=32) {
  if (avatar_hash) {
    return "https://cdn.discordapp.com/avatars/"+member_id+"/"+avatar_hash+"?size="+size;
  } else {
    return "https://cdn.discordapp.com/embed/avatars/" + (parseInt(member_id) % 5) + ".png";
  }
}
