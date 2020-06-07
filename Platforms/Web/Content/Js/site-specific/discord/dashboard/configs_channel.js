var ConfigsChannel = new (class {
  constructor() {
    this.modal_id = "#configs_channel_exeption_modal";
    this.list_id = "#exception_channel_list";
    this.phantom_class = ".exceptionchannel";
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
    var ConfigsChannelO = this;
    var req = {};
    req["guild_id"] = $("#guild_id").val();

    var endpoint = null;
    var modal_title = "[N/A]";

    switch (list_name.toLowerCase()) {
      case "level":
        endpoint = "leveldisabledchannels";
        modal_title = "Level disabled channels";
        break;

      case "normal":
        endpoint = "normaldisabledchannels";
        modal_title = "Normal-Command disabled channels";
        break;

      case "regular":
        endpoint = "regulardisabledchannels";
        modal_title = "Regular-Command disabled channels";
        break;

      case "quote":
        endpoint = "quotedisabledchannels";
        modal_title = "Quote-Command disabled channels";
        break;

      case "game":
        endpoint = "gameenabledchannels";
        modal_title = "Game-Command enabled channels";
        break;

      case "nsfw":
        endpoint = "nsfwenabledchannels";
        modal_title = "NSFW-Command enabled channels";
        break;
    }

    if (isEmpty(endpoint)) { throw `can't resolve listname: ${list_name}`; }

    $.get(`/api/discord/configs/${endpoint}/get`, req)
    .done(function (data) {

      var EntryList = $(ConfigsChannelO.list_id).html('');
      for (var entry of data.result) {
        var channel = DiscordDashboard.getDiscordChannelByID(entry.channel_id);
        var Template = $(`[phantom] ${ConfigsChannelO.phantom_class}`).clone();

        EntryList.append(Template);
      }

      // set stuff for later
      $(`${ConfigsChannelO.modal_id} [name=list_name]`).val(list_name);

      // set description
      $(`${ConfigsChannelO.modal_id} [modal-desc]`).hide();
      $(`${ConfigsChannelO.modal_id} [modal-desc=${list_name}]`).show();

      // set title
      $(`${ConfigsChannelO.modal_id} .modal-title`).text(modal_title);

      // show modal
      $(ConfigsChannelO.modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:`could not load configs for ${channel_list} channel exceptions`} );
    });
  }

});
