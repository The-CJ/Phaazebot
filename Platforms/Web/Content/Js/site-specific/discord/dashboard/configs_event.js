var ConfigsEvent = new (class {
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
      insertData("[location=configs_event]", data.result);

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load configs for events"} );
    })
  }

});
