var Configs = new(class {
  constructor() {
    this.blacklist = [];
    this.whitelist = [];
    this.except_roleslist = [];
    this.disable_chan_level = [];
    this.disable_chan_quote = [];
    this.disable_chan_normal = [];
    this.disable_chan_regular = [];
    this.enable_chan_game = [];
    this.enable_chan_nsfw = [];
  }

  show() {
    var guild_id = $("#guild_id").val();

    $.get("/api/discord/configs/get", {guild_id: guild_id})
    .done(function (data) {

      // insert current data
      insertData("[location=configs]", data.result);

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load configs"} );
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
      generalAPIErrorHandler( {data:data, msg:"error loading word link whitelist"} );
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
      generalAPIErrorHandler( {data:data, msg:"error loading word blacklist"} );
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
      generalAPIErrorHandler( {data:data, msg:"error loading execption roles"} );
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

  // disable level
  showDisableChanLevel() {
    var ConfigsO = this;
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/get", {guild_id: guild_id})
    .done(function (data) {
      ConfigsO.disable_chan_level = data.result.disabled_levelchannels;
      ConfigsO.buildDisableChanLevel(ConfigsO.disable_chan_level);
      $("#config_modal_disable_chan_level").modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading execption channels"} );
    })
  }

  buildDisableChanLevel(channel_list) {
    var EntryList = $("#config_modal_disable_chan_level .disablechanlevellist").html("");
    for (var entry of channel_list) {
      var EntryRow = $("[phantom] .disablechanlevel").clone();
      var channel = DiscordDashboard.getDiscordChannelByID(entry);
      EntryRow.find("[channel-id]").val(entry);
      EntryRow.find(".name").text( channel ? "#"+channel.name : "(DELETED CHANNEL)" );
      if (isEmpty(channel)) {
        EntryRow.addClass("deleted");
        EntryRow.attr("title", "This channel is deleted on the server and can be deleted here as well without any worries");
      }

      EntryList.append(EntryRow);
    }
  }

  addToDisableChanLevel() {
    var new_channel_id = $("#new_disable_chan_level").val();
    if (isEmpty(new_channel_id)) { return; }
    var req = {
      "disabled_levelchan_id": new_channel_id,
      "disabled_levelchan_action": "add"
    };
    var ConfigsO = this;
    var successfunc = function() {
      $("#new_disable_chan_level").val("");
      ConfigsO.disable_chan_level.push(new_channel_id.toLowerCase());
      ConfigsO.buildDisableChanLevel(ConfigsO.disable_chan_level);
    }
    var failfunc = function () {
      $("#new_disable_chan_level").val("");
    }

    this.update(req, successfunc, failfunc);
  }

  removeFromDisableChanLevel(HTMLButton) {
    var Entry = $(HTMLButton).closest(".disablechanlevel");
    var channel_id = Entry.find("[channel-id]").val();

    var req = {
      "disabled_levelchan_id": channel_id,
      "disabled_levelchan_action": "remove"
    };
    var ConfigsO = this;
    this.update(req, function () {
      var i = ConfigsO.disable_chan_level.indexOf(channel_id);
      ConfigsO.disable_chan_level.splice(i, 1);
      ConfigsO.buildDisableChanLevel(ConfigsO.disable_chan_level);
    });
  }

  // disable quote
  showDisableChanQuote() {
    var ConfigsO = this;
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/get", {guild_id: guild_id})
    .done(function (data) {
      ConfigsO.disable_chan_quote = data.result.disabled_quotechannels;
      ConfigsO.buildDisableChanQuote(ConfigsO.disable_chan_quote);
      $("#config_modal_disable_chan_quote").modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading quote channels"} );
    })
  }

  buildDisableChanQuote(channel_list) {
    var EntryList = $("#config_modal_disable_chan_quote .disablechanquotelist").html("");
    for (var entry of channel_list) {
      var EntryRow = $("[phantom] .disablechanquote").clone();
      var channel = DiscordDashboard.getDiscordChannelByID(entry);
      EntryRow.find("[channel-id]").val(entry);
      EntryRow.find(".name").text( channel ? "#"+channel.name : "(DELETED CHANNEL)" );
      if (isEmpty(channel)) {
        EntryRow.addClass("deleted");
        EntryRow.attr("title", "This channel is deleted on the server and can be deleted here as well without any worries");
      }

      EntryList.append(EntryRow);
    }
  }

  addToDisableChanQuote() {
    var new_channel_id = $("#new_disable_chan_quote").val();
    if (isEmpty(new_channel_id)) { return; }
    var req = {
      "disabled_quotechan_id": new_channel_id,
      "disabled_quotechan_action": "add"
    };
    var ConfigsO = this;
    var successfunc = function() {
      $("#new_disable_chan_quote").val("");
      ConfigsO.disable_chan_level.push(new_channel_id.toLowerCase());
      ConfigsO.buildDisableChanLevel(ConfigsO.disable_chan_level);
    }
    var failfunc = function () {
      $("#new_disable_chan_quote").val("");
    }

    this.update(req, successfunc, failfunc);
  }

  removeFromDisableChanQuote(HTMLButton) {
    var Entry = $(HTMLButton).closest(".disablechanquote");
    var channel_id = Entry.find("[channel-id]").val();

    var req = {
      "disabled_quotechan_id": channel_id,
      "disabled_quotechan_action": "remove"
    };
    var ConfigsO = this;
    this.update(req, function () {
      var i = ConfigsO.disable_chan_quote.indexOf(channel_id);
      ConfigsO.disable_chan_quote.splice(i, 1);
      ConfigsO.buildDisableChanQuote(ConfigsO.disable_chan_quote);
    });
  }

  // disable normal
  showDisableChanNormal() {
    var ConfigsO = this;
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/get", {guild_id: guild_id})
    .done(function (data) {
      ConfigsO.disable_chan_normal = data.result.disabled_normalchannels;
      ConfigsO.buildDisableChanNormal(ConfigsO.disable_chan_normal);
      $("#config_modal_disable_chan_normal").modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading normal channels"} );
    })
  }

  buildDisableChanNormal(channel_list) {
    var EntryList = $("#config_modal_disable_chan_normal .disablechannormallist").html("");
    for (var entry of channel_list) {
      var EntryRow = $("[phantom] .disablechannormal").clone();
      var channel = DiscordDashboard.getDiscordChannelByID(entry);
      EntryRow.find("[channel-id]").val(entry);
      EntryRow.find(".name").text( channel ? "#"+channel.name : "(DELETED CHANNEL)" );
      if (isEmpty(channel)) {
        EntryRow.addClass("deleted");
        EntryRow.attr("title", "This channel is deleted on the server and can be deleted here as well without any worries");
      }

      EntryList.append(EntryRow);
    }
  }

  addToDisableChanNormal() {
    var new_channel_id = $("#new_disable_chan_normal").val();
    if (isEmpty(new_channel_id)) { return; }
    var req = {
      "disabled_normalchan_id": new_channel_id,
      "disabled_normalchan_action": "add"
    };
    var ConfigsO = this;
    var successfunc = function() {
      $("#new_disable_chan_normal").val("");
      ConfigsO.disable_chan_level.push(new_channel_id.toLowerCase());
      ConfigsO.buildDisableChanLevel(ConfigsO.disable_chan_level);
    }
    var failfunc = function () {
      $("#new_disable_chan_normal").val("");
    }

    this.update(req, successfunc, failfunc);
  }

  removeFromDisableChanNormal(HTMLButton) {
    var Entry = $(HTMLButton).closest(".disablechannormal");
    var channel_id = Entry.find("[channel-id]").val();

    var req = {
      "disabled_normalchan_id": channel_id,
      "disabled_normalchan_action": "remove"
    };
    var ConfigsO = this;
    this.update(req, function () {
      var i = ConfigsO.disable_chan_normal.indexOf(channel_id);
      ConfigsO.disable_chan_normal.splice(i, 1);
      ConfigsO.buildDisableChanNormal(ConfigsO.disable_chan_normal);
    });
  }

  // disable regular
  showDisableChanRegular() {
    var ConfigsO = this;
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/get", {guild_id: guild_id})
    .done(function (data) {
      ConfigsO.disable_chan_regular = data.result.disabled_regularchannels;
      ConfigsO.buildDisableChanRegular(ConfigsO.disable_chan_regular);
      $("#config_modal_disable_chan_regular").modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading regular channels"} );
    })
  }

  buildDisableChanRegular(channel_list) {
    var EntryList = $("#config_modal_disable_chan_regular .disablechanregularlist").html("");
    for (var entry of channel_list) {
      var EntryRow = $("[phantom] .disablechanregular").clone();
      var channel = DiscordDashboard.getDiscordChannelByID(entry);
      EntryRow.find("[channel-id]").val(entry);
      EntryRow.find(".name").text( channel ? "#"+channel.name : "(DELETED CHANNEL)" );
      if (isEmpty(channel)) {
        EntryRow.addClass("deleted");
        EntryRow.attr("title", "This channel is deleted on the server and can be deleted here as well without any worries");
      }

      EntryList.append(EntryRow);
    }
  }

  addToDisableChanRegular() {
    var new_channel_id = $("#new_disable_chan_regular").val();
    if (isEmpty(new_channel_id)) { return; }
    var req = {
      "disabled_regularchan_id": new_channel_id,
      "disabled_regularchan_action": "add"
    };
    var ConfigsO = this;
    var successfunc = function() {
      $("#new_disable_chan_regular").val("");
      ConfigsO.disable_chan_level.push(new_channel_id.toLowerCase());
      ConfigsO.buildDisableChanLevel(ConfigsO.disable_chan_level);
    }
    var failfunc = function () {
      $("#new_disable_chan_regular").val("");
    }

    this.update(req, successfunc, failfunc);
  }

  removeFromDisableChanRegular(HTMLButton) {
    var Entry = $(HTMLButton).closest(".disablechanregular");
    var channel_id = Entry.find("[channel-id]").val();

    var req = {
      "disabled_regularchan_id": channel_id,
      "disabled_regularchan_action": "remove"
    };
    var ConfigsO = this;
    this.update(req, function () {
      var i = ConfigsO.disable_chan_regular.indexOf(channel_id);
      ConfigsO.disable_chan_regular.splice(i, 1);
      ConfigsO.buildDisableChanRegular(ConfigsO.disable_chan_regular);
    });
  }

  // enable game
  showEnableChanGame() {
    var ConfigsO = this;
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/get", {guild_id: guild_id})
    .done(function (data) {
      ConfigsO.enable_chan_game = data.result.enabled_gamechannels;
      ConfigsO.buildEnableChanGame(ConfigsO.enable_chan_game);
      $("#config_modal_enable_chan_game").modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading game channels"} );
    })
  }

  buildEnableChanGame(channel_list) {
    var EntryList = $("#config_modal_enable_chan_game .enablechangamelist").html("");
    for (var entry of channel_list) {
      var EntryRow = $("[phantom] .enablechangame").clone();
      var channel = DiscordDashboard.getDiscordChannelByID(entry);
      EntryRow.find("[channel-id]").val(entry);
      EntryRow.find(".name").text( channel ? "#"+channel.name : "(DELETED CHANNEL)" );
      if (isEmpty(channel)) {
        EntryRow.addClass("deleted");
        EntryRow.attr("title", "This channel is deleted on the server and can be deleted here as well without any worries");
      }

      EntryList.append(EntryRow);
    }
  }

  addToEnableChanGame() {
    var new_channel_id = $("#new_enable_chan_game").val();
    if (isEmpty(new_channel_id)) { return; }
    var req = {
      "enabled_gamechan_id": new_channel_id,
      "enabled_gamechan_action": "add"
    };
    var ConfigsO = this;
    var successfunc = function() {
      $("#new_enable_chan_game").val("");
      ConfigsO.enable_chan_game.push(new_channel_id.toLowerCase());
      ConfigsO.buildEnableChanGame(ConfigsO.enable_chan_game);
    }
    var failfunc = function () {
      $("#new_enable_chan_game").val("");
    }

    this.update(req, successfunc, failfunc);
  }

  removeFromEnableChanGame(HTMLButton) {
    var Entry = $(HTMLButton).closest(".enablechangame");
    var channel_id = Entry.find("[channel-id]").val();

    var req = {
      "enabled_gamechan_id": channel_id,
      "enabled_gamechan_action": "remove"
    };
    var ConfigsO = this;
    this.update(req, function () {
      var i = ConfigsO.enable_chan_game.indexOf(channel_id);
      ConfigsO.enable_chan_game.splice(i, 1);
      ConfigsO.buildEnableChanGame(ConfigsO.enable_chan_game);
    });
  }

  // enable nsfw
  showEnableChanNSFW() {
    var ConfigsO = this;
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/get", {guild_id: guild_id})
    .done(function (data) {
      ConfigsO.enable_chan_nsfw = data.result.enabled_nsfwchannels;
      ConfigsO.buildEnableChanNSFW(ConfigsO.enable_chan_nsfw);
      $("#config_modal_enable_chan_nsfw").modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading nsfw channels"} );
    })
  }

  buildEnableChanNSFW(channel_list) {
    console.log(channel_list);
    var EntryList = $("#config_modal_enable_chan_nsfw .enablechannsfwlist").html("");
    for (var entry of channel_list) {
      var EntryRow = $("[phantom] .enablechannsfw").clone();
      var channel = DiscordDashboard.getDiscordChannelByID(entry);
      EntryRow.find("[channel-id]").val(entry);
      EntryRow.find(".name").text( channel ? "#"+channel.name : "(DELETED CHANNEL)" );
      if (isEmpty(channel)) {
        EntryRow.addClass("deleted");
        EntryRow.attr("title", "This channel is deleted on the server and can be deleted here as well without any worries");
      }

      EntryList.append(EntryRow);
    }
  }

  addToEnableChanNSFW() {
    var new_channel_id = $("#new_enable_chan_nsfw").val();
    if (isEmpty(new_channel_id)) { return; }
    var req = {
      "enabled_nsfwchan_id": new_channel_id,
      "enabled_nsfwchan_action": "add"
    };
    var ConfigsO = this;
    var successfunc = function() {
      $("#new_enable_chan_nsfw").val("");
      ConfigsO.enable_chan_nsfw.push(new_channel_id.toLowerCase());
      ConfigsO.buildEnableChanNSFW(ConfigsO.enable_chan_nsfw);
    }
    var failfunc = function () {
      $("#new_enable_chan_nsfw").val("");
    }

    this.update(req, successfunc, failfunc);
  }

  removeFromEnableChanNSFW(HTMLButton) {
    var Entry = $(HTMLButton).closest(".enablechannsfw");
    var channel_id = Entry.find("[channel-id]").val();

    var req = {
      "enabled_nsfwchan_id": channel_id,
      "enabled_nsfwchan_action": "remove"
    };
    var ConfigsO = this;
    this.update(req, function () {
      var i = ConfigsO.enable_chan_nsfw.indexOf(channel_id);
      ConfigsO.enable_chan_nsfw.splice(i, 1);
      ConfigsO.buildEnableChanNSFW(ConfigsO.enable_chan_nsfw);
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
      generalAPIErrorHandler( {data:data, msg:"error updating configs"} );
      if (fail_function) { fail_function.call() }
    })
  }

});
