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

    var endpoint = null;

    switch (list_name.toLowerCase()) {
      case "level":
        endpoint = "leveldisabledchannels";
        break;

      case "normal":
        endpoint = "normaldisabledchannels";
        break;

      case "regular":
        endpoint = "regulardisabledchannels";
        break;

      case "quote":
        endpoint = "quotedisabledchannels";
        break;

      case "game":
        endpoint = "gameenabledchannels";
        break;

      case "nsfw":
        endpoint = "nsfwenabledchannels";
        break;
    }

    if (isEmpty(endpoint)) { throw `can't resolve listname: ${list_name}`; }

    $.get(`/api/discord/configs/${endpoint}/get`, req)
    .done(function (data) {

      console.log(data);

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load configs for channel"} );
    });
  }

});
