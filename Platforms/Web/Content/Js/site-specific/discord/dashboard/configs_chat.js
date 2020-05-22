var ConfigsChat = new(class {
  constructor() {
    this.word_blacklist_modal_id = "#configs_chat_word_blacklist_modal";
    this.word_blacklist_phantom_class = ".blacklistword";
    this.word_blacklist_list_id = "#blacklist_list";
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
        Template.attr("word_id", entry.word_id);
        insertData(Template, entry);
        EntryList.append(Template);
      }
      $(ConfigsChatO.word_blacklist_modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error loading word blacklist"} );
    })
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
