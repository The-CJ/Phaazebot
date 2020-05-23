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

  // edit
  editContentBox(HTMLElement) {
    var ContentBox = $(HTMLElement).closest(".content-box");
    var data = extractData(ContentBox);
    this.edit(data);
  }

  edit(update) {
    update["guild_id"] = $("#guild_id").val();

    $.post("/api/discord/configs/edit", update)
    .done(function (data) {

      insertData("[location=configs_event]", data.changes, true);
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error updating configs for event"} );
    })
  }


});
