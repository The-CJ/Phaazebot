var ConfigsMaster = new (class {
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
      insertData("[location=configs_master]", data.result);

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load configs for master"} );
    })
  }

  // edit
  toggleOption(option) {
    if (!option) { return; }

    var current_value = $(`[location=configs_master] [name=${option}]`).attr("value");
    var new_value = oppositeValue(current_value);

    var req = {};
    req[option] = new_value;
    this.edit( req );
  }

  edit(update) {
    update["guild_id"] = $("#guild_id").val();

    $.post("/api/discord/configs/edit", update)
    .done(function (data) {

      insertData("[location=configs_master]", data.changes, true);
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error updating configs for master"} );
    })
  }


});
