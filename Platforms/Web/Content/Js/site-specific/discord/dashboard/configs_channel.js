var ConfigsChannel = new (class {
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
      insertData("[location=configs_channel]", data.result);

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load configs for channel"} );
    })
  }

  showChannelList(list_name) {

    var req = {};
    req["guild_id"] = $("#guild_id").val();

    $.get(`/api/discord/configs/${channel_list_endpoint}/get`, req)
    .done(function (data) {

      console.log(data);

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load configs for channel"} );
    });
  }

});
