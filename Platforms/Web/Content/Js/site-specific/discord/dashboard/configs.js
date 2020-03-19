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

    this.whitelist_modal_id = "#config_modal_whitelist_links";
    this.whitelist_phantom_class = ".whitelistlink";

    this.blacklist_modal_id = "#config_modal_blacklist_words";
    this.blacklist_phantom_class = ".blacklistword";

    this.exceptionrole_modal_id = "#config_modal_exeption_roles";
    this.exceptionrole_phantom_class = ".exceptionrole";

    this.disable_level_modal_id = "#config_modal_disable_chan_level";
    this.disable_level_phantom_class = ".disablechanlevel";

    this.disable_quote_modal_id = "#config_modal_disable_chan_quote";
    this.disable_quote_phantom_class = ".disablechanquote";

    this.disable_normal_modal_id = "#config_modal_disable_chan_normal";
    this.disable_normal_phantom_class = ".disablechannormal";

    this.disable_regular_modal_id = "#config_modal_disable_chan_regular";
    this.disable_regular_phantom_class = ".disablechanregular";

    this.enable_game_modal_id = "#config_modal_enable_chan_game";
    this.enable_game_phantom_class = ".enablechangame";

    this.enable_nsfw_modal_id = "#config_modal_enable_chan_nsfw";
    this.enable_nsfw_phantom_class = ".enablechannsfw";

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

  // links whitelist
  showLinkWhitelist() {
    var ConfigsO = this;
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/whitelistedlinks/get", {guild_id: guild_id})
    .done(function (data) {
      ConfigsO.whitelist = data.result;
      ConfigsO.buildLinkWhitelist(ConfigsO.whitelist);
      $(ConfigsO.whitelist_modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading link whitelist"} );
    })
  }

  buildLinkWhitelist(whitelist_links) {
    var EntryList = $(`${this.whitelist_modal_id} .modal-itemlist`).html("");
    for (var entry of whitelist_links) {
      var EntryRow = $(`[phantom] ${this.whitelist_phantom_class}`).clone();
      EntryRow.attr("link-id", entry.link_id);
      EntryRow.find(".link").text(entry.link);
      EntryList.append(EntryRow);
    }
  }

  addToLinkWhitelist() {
    var guild_id = $("#guild_id").val();
    var new_link = $("#new_whitelistlink").val();
    if (isEmpty(new_link)) { return; }
    var ConfigsO = this;
    var req = {
      "link": new_link,
      "guild_id": guild_id
    };

    $.post("/api/discord/configs/whitelistedlinks/create", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      $("#new_whitelistlink").val("");
      ConfigsO.showLinkWhitelist();
    })
    .fail(function (data) {
      $("#new_whitelistlink").val("");
      generalAPIErrorHandler( {data:data, msg:"error adding link to whitelist"} );
    });

  }

  removeFromLinkWhitelist(HTMLButton) {
    var guild_id = $("#guild_id").val();
    var Entry = $(HTMLButton).closest(this.whitelist_phantom_class);
    var link_id = Entry.attr("link-id");
    if (isEmpty(link_id)) { return; }
    var ConfigsO = this;
    var req = {
      "link_id": link_id,
      "guild_id": guild_id
    };

    $.post("/api/discord/configs/whitelistedlinks/delete", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      ConfigsO.showLinkWhitelist();
    })
    .fail(function (data) {
      $("#new_whitelistlink").val("");
      generalAPIErrorHandler( {data:data, msg:"error removing link from whitelist"} );
    });

  }

  // blacklist
  showWordBlacklist() {
    var ConfigsO = this;
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/blacklistedwords/get", {guild_id: guild_id})
    .done(function (data) {
      ConfigsO.blacklist = data.result;
      ConfigsO.buildWordBlacklist(ConfigsO.blacklist);
      $(ConfigsO.blacklist_modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading word blacklist"} );
    })
  }

  buildWordBlacklist(blacklist_blacklistwords) {
    var EntryList = $(`${this.blacklist_modal_id} .modal-itemlist`).html("");
    for (var entry of blacklist_blacklistwords) {
      var EntryRow = $(`[phantom] ${this.blacklist_phantom_class}`).clone();
      EntryRow.attr("word-id", entry.word_id);
      EntryRow.find(".word").text(entry.word);
      EntryList.append(EntryRow);
    }
  }

  addToBlacklist() {
    var guild_id = $("#guild_id").val();
    var new_word = $("#new_blacklistword").val();
    if (isEmpty(new_word)) { return; }
    var ConfigsO = this;
    var req = {
      "word": new_word,
      "guild_id": guild_id
    };

    $.post("/api/discord/configs/blacklistedwords/create", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      $("#new_blacklistword").val("");
      ConfigsO.showWordBlacklist();
    })
    .fail(function (data) {
      $("#new_blacklistword").val("");
      generalAPIErrorHandler( {data:data, msg:"error adding word to blacklist"} );
    });

  }

  removeFromBlacklist(HTMLButton) {
    var guild_id = $("#guild_id").val();
    var Entry = $(HTMLButton).closest(this.blacklist_phantom_class);
    var word_id = Entry.attr("word-id");
    if (isEmpty(word_id)) { return; }
    var ConfigsO = this;
    var req = {
      "word_id": word_id,
      "guild_id": guild_id
    };

    $.post("/api/discord/configs/blacklistedwords/delete", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      ConfigsO.showWordBlacklist();
    })
    .fail(function (data) {
      $("#new_blacklistword").val("");
      generalAPIErrorHandler( {data:data, msg:"error removing word from blacklist"} );
    });
  }

  // roles
  showExecptionRoles() {
    var ConfigsO = this;
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/exceptionroles/get", {guild_id: guild_id})
    .done(function (data) {
      ConfigsO.except_roleslist = data.result;
      ConfigsO.buildExecptionRoles(ConfigsO.except_roleslist);
      $(ConfigsO.exceptionrole_modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading execption roles"} );
    })
  }

  buildExecptionRoles(exceptionroles_roles) {
    var EntryList = $(`${this.exceptionrole_modal_id} .modal-itemlist`).html("");
    for (var entry of exceptionroles_roles) {
      var EntryRow = $(`[phantom] ${this.exceptionrole_phantom_class}`).clone();
      var role = DiscordDashboard.getDiscordRoleByID(entry.role_id);
      EntryRow.attr("entry-id", entry.exceptionrole_id);
      EntryRow.find(".name").text( role ? role.name : "(DELETED ROLE)" );
      if (isEmpty(role)) {
        EntryRow.addClass("deleted");
        EntryRow.attr("title", "This role is deleted on the server and can be deleted here as well without any worries");
      }
      EntryList.append(EntryRow);
    }
  }

  addToExecptionRoles() {
    var guild_id = $("#guild_id").val();
    var new_role_id = $("#new_exceptionrole").val();
    if (isEmpty(new_role_id)) { return; }
    var ConfigsO = this;
    var req = {
      "role_id": new_role_id,
      "guild_id": guild_id
    };

    $.post("/api/discord/configs/exceptionroles/create", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      $("#new_exceptionrole").val("");
      ConfigsO.showExecptionRoles();
    })
    .fail(function (data) {
      $("#new_exceptionrole").val("");
      generalAPIErrorHandler( {data:data, msg:"error adding role to exceptionroles"} );
    });
  }

  removeFromExecptionRoles(HTMLButton) {
    var guild_id = $("#guild_id").val();
    var Entry = $(HTMLButton).closest(this.exceptionrole_phantom_class);
    var entry_id = Entry.attr("entry-id");
    if (isEmpty(entry_id)) { return; }
    var ConfigsO = this;
    var req = {
      "exceptionrole_id": entry_id,
      "guild_id": guild_id
    };

    $.post("/api/discord/configs/exceptionroles/delete", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      ConfigsO.showExecptionRoles();
    })
    .fail(function (data) {
      $("#new_exceptionrole").val("");
      generalAPIErrorHandler( {data:data, msg:"error removing entry from exceptionroles"} );
    });
  }

  // disable level
  showDisableChanLevel() {
    var ConfigsO = this;
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/leveldisabledchannels/get", {guild_id: guild_id})
    .done(function (data) {
      ConfigsO.disable_chan_level = data.result;
      ConfigsO.buildDisableChanLevel(ConfigsO.disable_chan_level);
      $(ConfigsO.disable_level_modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading level disabled channels"} );
    })
  }

  buildDisableChanLevel(channel_list) {
    var EntryList = $(`${this.disable_level_modal_id} .modal-itemlist`).html("");
    for (var entry of channel_list) {
      var EntryRow = $(`[phantom] ${this.disable_level_phantom_class}`).clone();
      var channel = DiscordDashboard.getDiscordChannelByID(entry.channel_id);
      EntryRow.attr("entry-id", entry.entry_id);
      EntryRow.find(".name").text( channel ? "#"+channel.name : "(DELETED CHANNEL)" );
      if (isEmpty(channel)) {
        EntryRow.addClass("deleted");
        EntryRow.attr("title", "This channel is deleted on the server and can be deleted here as well without any worries");
      }
      EntryList.append(EntryRow);
    }
  }

  addToDisableChanLevel() {
    var guild_id = $("#guild_id").val();
    var new_channel_id = $("#new_disable_chan_level").val();
    if (isEmpty(new_channel_id)) { return; }
    var ConfigsO = this;
    var req = {
      "channel_id": new_channel_id,
      "guild_id": guild_id
    };

    $.post("/api/discord/configs/leveldisabledchannels/create", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      $("#new_disable_chan_level").val("");
      ConfigsO.showDisableChanLevel();
    })
    .fail(function (data) {
      $("#new_disable_chan_level").val("");
      generalAPIErrorHandler( {data:data, msg:"error adding channel to level disabled list"} );
    });
  }

  removeFromDisableChanLevel(HTMLButton) {
    var guild_id = $("#guild_id").val();
    var Entry = $(HTMLButton).closest(this.disable_level_phantom_class);
    var entry_id = Entry.attr("entry-id");
    if (isEmpty(entry_id)) { return; }
    var ConfigsO = this;
    var req = {
      "entry_id": entry_id,
      "guild_id": guild_id
    };

    $.post("/api/discord/configs/leveldisabledchannels/delete", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      ConfigsO.showDisableChanLevel();
    })
    .fail(function (data) {
      $("#new_disable_chan_level").val("");
      generalAPIErrorHandler( {data:data, msg:"error removing entry from level disabled list"} );
    });
  }

  // disable quote
  showDisableChanQuote() {
    var ConfigsO = this;
    var guild_id = $("#guild_id").val();
    $.get("/api/discord/configs/quotedisabledchannels/get", {guild_id: guild_id})
    .done(function (data) {
      ConfigsO.disable_chan_quote = data.result;
      ConfigsO.buildDisableChanQuote(ConfigsO.disable_chan_quote);
      $(ConfigsO.disable_quote_modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading quote disabled channels"} );
    })
  }

  buildDisableChanQuote(channel_list) {
    var EntryList = $(`${this.disable_quote_modal_id} .modal-itemlist`).html("");
    for (var entry of channel_list) {
      var EntryRow = $(`[phantom] ${this.disable_quote_phantom_class}`).clone();
      var channel = DiscordDashboard.getDiscordChannelByID(entry.channel_id);
      EntryRow.attr("entry-id", entry.entry_id);
      EntryRow.find(".name").text( channel ? "#"+channel.name : "(DELETED CHANNEL)" );
      if (isEmpty(channel)) {
        EntryRow.addClass("deleted");
        EntryRow.attr("title", "This channel is deleted on the server and can be deleted here as well without any worries");
      }
      EntryList.append(EntryRow);
    }
  }

  addToDisableChanQuote() {
    var guild_id = $("#guild_id").val();
    var new_channel_id = $("#new_disable_chan_quote").val();
    if (isEmpty(new_channel_id)) { return; }
    var ConfigsO = this;
    var req = {
      "channel_id": new_channel_id,
      "guild_id": guild_id
    };

    $.post("/api/discord/configs/quotedisabledchannels/create", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      $("#new_disable_chan_quote").val("");
      ConfigsO.showDisableChanQuote();
    })
    .fail(function (data) {
      $("#new_disable_chan_quote").val("");
      generalAPIErrorHandler( {data:data, msg:"error adding channel to quote disabled list"} );
    });
  }

  removeFromDisableChanQuote(HTMLButton) {
    var guild_id = $("#guild_id").val();
    var Entry = $(HTMLButton).closest(this.disable_quote_phantom_class);
    var entry_id = Entry.attr("entry-id");
    if (isEmpty(entry_id)) { return; }
    var ConfigsO = this;
    var req = {
      "entry_id": entry_id,
      "guild_id": guild_id
    };

    $.post("/api/discord/configs/quotedisabledchannels/delete", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      ConfigsO.showDisableChanQuote();
    })
    .fail(function (data) {
      $("#new_disable_chan_quote").val("");
      generalAPIErrorHandler( {data:data, msg:"error removing entry from quote disabled list"} );
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
      $(Configs.disable_normal_modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading normal channels"} );
    })
  }

  buildDisableChanNormal(channel_list) {
    var EntryList = $(`${this.disable_normal_modal_id} .modal-itemlist`).html("");
    for (var entry of channel_list) {
      var EntryRow = $(`[phantom] ${this.disable_normal_phantom_class}`).clone();
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
      ConfigsO.disable_chan_normal.push(new_channel_id);
      ConfigsO.buildDisableChanNormal(ConfigsO.disable_chan_normal);
    }
    var failfunc = function () {
      $("#new_disable_chan_normal").val("");
    }

    this.update(req, successfunc, failfunc);
  }

  removeFromDisableChanNormal(HTMLButton) {
    var Entry = $(HTMLButton).closest(this.disable_normal_phantom_class);
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
      $(ConfigsO.disable_regular_modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading regular channels"} );
    })
  }

  buildDisableChanRegular(channel_list) {
    var EntryList = $(`${this.disable_regular_modal_id} .modal-itemlist`).html("");
    for (var entry of channel_list) {
      var EntryRow = $(`[phantom] ${this.disable_regular_phantom_class}`).clone();
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
      ConfigsO.disable_chan_regular.push(new_channel_id);
      ConfigsO.buildDisableChanRegular(ConfigsO.disable_chan_regular);
    }
    var failfunc = function () {
      $("#new_disable_chan_regular").val("");
    }

    this.update(req, successfunc, failfunc);
  }

  removeFromDisableChanRegular(HTMLButton) {
    var Entry = $(HTMLButton).closest(this.disable_regular_phantom_class);
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
      $(ConfigsO.enable_game_modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading game channels"} );
    })
  }

  buildEnableChanGame(channel_list) {
    var EntryList = $(`${this.enable_game_modal_id} .modal-itemlist`).html("");
    for (var entry of channel_list) {
      var EntryRow = $(`[phantom] ${this.enable_game_phantom_class}`).clone();
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
      ConfigsO.enable_chan_game.push(new_channel_id);
      ConfigsO.buildEnableChanGame(ConfigsO.enable_chan_game);
    }
    var failfunc = function () {
      $("#new_enable_chan_game").val("");
    }

    this.update(req, successfunc, failfunc);
  }

  removeFromEnableChanGame(HTMLButton) {
    var Entry = $(HTMLButton).closest(this.enable_game_phantom_class);
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
      $(Configs.enable_nsfw_modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading nsfw channels"} );
    })
  }

  buildEnableChanNSFW(channel_list) {
    var EntryList = $(`${this.enable_nsfw_modal_id} .modal-itemlist`).html("");
    for (var entry of channel_list) {
      var EntryRow = $(`[phantom] ${this.enable_nsfw_phantom_class}`).clone();
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
    var Entry = $(HTMLButton).closest(this.enable_nsfw_phantom_class);
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

      insertData("[location=configs]", data.update, true);
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});

      if (success_function) { success_function.call() }

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error updating configs"} );
      if (fail_function) { fail_function.call() }
    })
  }

});
