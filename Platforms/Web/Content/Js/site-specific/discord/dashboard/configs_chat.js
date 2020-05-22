var ConfigsChat = new(class {
  constructor() {
    this.word_blacklist_modal_id = "#configs_chat_word_blacklist_modal";
    this.word_blacklist_phantom_class = ".blacklistword";
    this.word_blacklist_list_id = "#blacklist_list";

    this.link_whitelist_modal_id = "#configs_chat_link_whitelist_modal";
    this.link_whitelist_phantom_class = ".whitelistlink";
    this.link_whitelist_list_id = "#whitelist_list";

    this.exeption_role_modal_id = "#configs_chat_exeption_role_modal";
    this.exeption_role_phantom_class = ".exceptionrole";
    this.exeption_role_list_id = "#exceptionrole_list";

  }

  show() {
    this.load();
  }

  load(x={}) {
    x["guild_id"] = $("#guild_id").val();

    $.get("/api/discord/configs/get", x)
    .done(function (data) {

      // insert current data
      insertData("[location=configs_chat]", data.result);

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load configs for chat"} );
    })
  }

  // show
  showWordBlacklist(x={}) {
    var ConfigsChatO = this;
    x["guild_id"] = $("#guild_id").val();
    $.get("/api/discord/configs/blacklistedwords/get", x)
    .done(function (data) {
      var EntryList = $(ConfigsChatO.word_blacklist_list_id).html('');
      for (var entry of data.result) {
        var Template = $(`[phantom] ${ConfigsChatO.word_blacklist_phantom_class}`).clone();
        Template.attr("word-id", entry.word_id);
        insertData(Template, entry);
        EntryList.append(Template);
      }
      $(ConfigsChatO.word_blacklist_modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading word blacklist"} );
    })
  }

  showLinkWhitelist(x={}) {
    var ConfigsChatO = this;
    x["guild_id"] = $("#guild_id").val();
    $.get("/api/discord/configs/whitelistedlinks/get", x)
    .done(function (data) {
      var EntryList = $(ConfigsChatO.link_whitelist_list_id).html('');
      for (var entry of data.result) {
        var Template = $(`[phantom] ${ConfigsChatO.link_whitelist_phantom_class}`).clone();
        Template.attr("link-id", entry.link_id);
        insertData(Template, entry);
        EntryList.append(Template);
      }
      $(ConfigsChatO.link_whitelist_modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading link whitelist"} );
    })
  }

  showExecptionRoles(x={}) {
    var ConfigsChatO = this;
    x["guild_id"] = $("#guild_id").val();
    $.get("/api/discord/configs/exceptionroles/get", x)
    .done(function (data) {
      var EntryList = $(ConfigsChatO.exeption_role_list_id).html('');
      for (var entry of data.result) {
        var role = DiscordDashboard.getDiscordRoleByID(entry.role_id);
        var Template = $(`[phantom] ${ConfigsChatO.exeption_role_phantom_class}`).clone();
        Template.attr("entry-id", entry.exceptionrole_id);
        Template.find("[name=role_name]").text( role ? role.name : "(DELETED ROLE)" );
        if (isEmpty(role)) {
          Template.addClass("deleted");
          Template.attr("title", "This role is deleted on the server and can be deleted here as well without any worries");
        }
        EntryList.append(Template);
      }
      $(ConfigsChatO.exeption_role_modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading role whitelist"} );
    })
  }

  // create
  createWordBlacklistEntry() {
    var ConfigsChatO = this;
    var new_word = $("#new_blacklistword").val();
    if (isEmpty(new_word)) { return; }
    var req = {
      "guild_id": $("#guild_id").val(),
      "word": new_word
    };

    $.get("/api/discord/configs/blacklistedwords/create", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      $("#new_blacklistword").val("");
      ConfigsChatO.showWordBlacklist();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error adding word to blacklist"} );
    });

  }

  createLinkWhitelistEntry() {
    var ConfigsChatO = this;
    var new_link = $("#new_whitelistlink").val();
    if (isEmpty(new_link)) { return; }
    var req = {
      "guild_id": $("#guild_id").val(),
      "link": new_link
    };

    $.get("/api/discord/configs/whitelistedlinks/create", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      $("#new_whitelistlink").val("");
      ConfigsChatO.showLinkWhitelist();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error adding link to whitelist"} );
    });

  }

  createExecptionRolesEntry() {
    var ConfigsChatO = this;
    var new_role_id = $("#new_exceptionrole").val();
    if (isEmpty(new_role_id)) { return; }
    var req = {
      "guild_id": $("#guild_id").val(),
      "role_id": new_role_id
    };

    $.get("/api/discord/configs/exceptionroles/create", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      $("#new_exceptionrole").val("");
      ConfigsChatO.showExecptionRoles();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error adding role to whitelist"} );
    });

  }

  // delete
  deleteWordBlacklistEntry(HTMLRow) {
    var ConfigsChatO = this;
    var word_id = $(HTMLRow).closest(ConfigsChatO.word_blacklist_phantom_class).attr("word-id");
    if (isEmpty(word_id)) { return; }
    var req = {
      "guild_id": $("#guild_id").val(),
      "word_id": word_id
    };

    $.post("/api/discord/configs/blacklistedwords/delete", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      ConfigsChatO.showWordBlacklist();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error removing word from blacklist"} );
    });

  }

  deleteLinkWhitelistEntry(HTMLRow) {
    var ConfigsChatO = this;
    var link_id = $(HTMLRow).closest(ConfigsChatO.link_whitelist_phantom_class).attr("link-id");
    if (isEmpty(link_id)) { return; }
    var req = {
      "guild_id": $("#guild_id").val(),
      "link_id": link_id
    };

    $.post("/api/discord/configs/whitelistedlinks/delete", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      ConfigsChatO.showLinkWhitelist();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error removing link from whitelist"} );
    });

  }

  deleteExecptionRolesEntry(HTMLRow) {
    var ConfigsChatO = this;
    var entry_id = $(HTMLRow).closest(ConfigsChatO.exeption_role_phantom_class).attr("entry-id");
    if (isEmpty(entry_id)) { return; }
    var req = {
      "guild_id": $("#guild_id").val(),
      "exceptionrole_id": entry_id
    };

    $.post("/api/discord/configs/exceptionroles/delete", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      ConfigsChatO.showExecptionRoles();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error removing role from whitelist"} );
    });

  }

  // edit
  toggleLinks() {
    var current_value = $("[location=configs_chat] [name=blacklist_ban_links]").attr("value");
    var new_value = oppositeValue(current_value);
    this.edit( {blacklist_ban_links: new_value} );
  }

  editPunishment() {
    var new_value = $("[location=configs_chat] [name=blacklist_punishment]").val();
    this.edit( {blacklist_punishment: new_value} );
  }

  edit(update) {
    update["guild_id"] = $("#guild_id").val();

    $.post("/api/discord/configs/edit", update)
    .done(function (data) {

      insertData("[location=configs_chat]", data.changes, true);
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error updating configs for chat"} );
    })
  }

});
