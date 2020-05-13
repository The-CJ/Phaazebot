var ConfigsChat = new(class {
  constructor() {

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
