var TwitchAlerts = new (class {
  constructor() {
    this.modal_id = "#alert_modal";
    this.list_id = "#twitchalert_list";
    this.total_field_id = "#alert_amount";
    this.phantom_class = ".twitchalert";
    this.twitchbase = "https://twitch.tv/";

    this.default_limit = 10;
    this.default_page = 0;

    this.current_limit = 0;
    this.current_page = 0;
    this.current_max_page = 0;
  }

  show() {
    // loads in default values or taken from url
    let limit = DynamicURL.get("alerts[limit]") || this.default_limit;
    let page = DynamicURL.get("alerts[page]") || this.default_page;

    var req = {
      limit: limit,
      offset: (page * limit)
    };

    this.load( req );
  }

  load(x={}) {
    var TwitchAlertsO = this;
    x["guild_id"] = $("#guild_id").val();

    $.get("/api/discord/twitchalerts/get", x)
    .done(function (data) {

      // update view
      TwitchAlertsO.updatePageIndexButtons(data);

      var AlertList = $(TwitchAlertsO.list_id).html("");
      $(TwitchAlerts.total_field_id).text(data.total);

      for (var alert of data.result) {
        var Template = $(`[phantom] ${TwitchAlertsO.phantom_class}`).clone();

        var twitch_name = alert.twitch_channel_name ? alert.twitch_channel_name : `Unknown channel name, ID: ${alert.twitch_channel_id}`;
        var discord_channel = DiscordDashboard.getDiscordChannelByID(alert.discord_channel_id);

        Template.find("[name=discord_channel]").text(discord_channel ? "#"+discord_channel.name : "(DELETED CHANNEL)");
        Template.find("[name=twitch_channel]").text(twitch_name);
        Template.attr("alert-id", alert.alert_id);

        if (isEmpty(discord_channel)) {
          Template.addClass("red");
          Template.attr("title", "This channel is deleted on the server and can be deleted here as well without any worries");
        }

        AlertList.append(Template);
      }
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load twitchalerts"} );
    })
  }

  // utils
  nextPage(last=false) {
    this.current_page += 1;
    var search = extractData("[location=twitch_alerts] .controlls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  prevPage(first=false) {
    this.current_page -= 1;
    if (first) { this.current_page = 0; }

    var search = extractData("[location=twitch_alerts] .controlls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  updatePageIndexButtons(data) {
    this.current_limit = data.limit;
    this.current_page = data.offset / data.limit;
    this.current_max_page = (data.total / data.limit);
    this.current_max_page = parseInt(this.current_max_page)

    // update limit url if needed
    if (this.current_limit != this.default_limit) {
      DynamicURL.set("alerts[limit]", this.current_limit);
    } else {
      DynamicURL.set("alerts[limit]", null);
    }

    // update page url if needed
    if (this.current_page != this.default_page) {
      DynamicURL.set("alerts[page]", this.current_page);
    } else {
      DynamicURL.set("alerts[page]", null);
    }

    // update html elements
    $("[location=twitch_alerts] [name=limit]").val(this.current_limit);
    $("[location=twitch_alerts] .pages .prev").attr("disabled", (this.current_page <= 0) );
    $("[location=twitch_alerts] .pages .next").attr("disabled", (this.current_page >= this.current_max_page) );
    $("[location=twitch_alerts] .pages .page").text(this.current_page+1);
  }

  // create
  createModal() {
    resetInput(this.modal_id);
    $(this.modal_id).attr("mode", "create");
    $(this.modal_id).modal("show");
  }

  create() {
    var TwitchAlertsO = this;
    var req = extractData(TwitchAlertsO.modal_id);
    req["guild_id"] = $("#guild_id").val();

    $.post("/api/discord/twitchalerts/create", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success});
      $(TwitchAlertsO.modal_id).modal("hide");
      TwitchAlertsO.show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not create alert"} );
    })
  }

  // edit
  editModal(HTMLButton) {
    var TwitchAlertsO = this;

    var req = {
      "guild_id": $("#guild_id").val(),
      "alert_id": $(HTMLButton).closest(TwitchAlertsO.phantom_class).attr("alert-id")
    };
    $.get("/api/discord/twitchalerts/get", req)
    .done(function (data) {

      $(TwitchAlertsO.modal_id).attr("mode", "edit");

      var alert = data.result.pop();
      var twitch_link = `${TwitchAlertsO.twitchbase}${alert.twitch_channel_name}`;
      var discord_channel = DiscordDashboard.getDiscordChannelByID(alert.discord_channel_id);

      $(`${TwitchAlertsO.modal_id} [name=twitch_link]`).attr("href", twitch_link).text(twitch_link);

      alert.discord_channel_name = discord_channel ? `#${discord_channel.name}` : "(DELETED CHANNEL)";

      insertData(TwitchAlertsO.modal_id, alert);
      $(TwitchAlertsO.modal_id).modal("show");

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load twitchalert"} );
    });

  }

  edit() {
    var TwitchAlertsO = this;

    var req = extractData(TwitchAlertsO.modal_id);
    req["guild_id"] = $("#guild_id").val();;

    $.post("/api/discord/twitchalerts/edit", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success});
      $(TwitchAlertsO.modal_id).modal("hide");
      TwitchAlertsO.show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not edit alert"} );
    })
  }

  // delete
  deleteFromList(HTMLButton) {
    let alert_id = $(HTMLButton).closest(this.phantom_class).attr("alert-id");
    this.delete(alert_id);
  }

  deleteFromModal() {
    let alert_id = $(`${this.modal_id} [name=alert_id]`).val();
    this.delete(alert_id);
  }

  delete(alert_id) {
    var c = confirm("Are you sure you want to delete this twitch alert?");
    if (!c) {return;}

    var TwitchAlertsO = this;

    var req = {
      "guild_id": $("#guild_id").val(),
      "alert_id": alert_id
    };

    $.post("/api/discord/twitchalerts/delete", req)
    .done(function (data) {
      $(TwitchAlertsO.modal_id).modal("hide");
      TwitchAlertsO.show();
      Display.showMessage({content: data.msg, color:Display.color_success});
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not delete alert"} );
    })
  }

});
