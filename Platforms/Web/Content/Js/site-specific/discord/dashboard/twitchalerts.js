var TwitchAlerts = new (class {
  constructor() {

  }

  show(x={}) {
    var TwitchAlertsO = this;
    var guild_id = $("#guild_id").val();
    // var offset = x["offset"] ? x["offset"] : 0; // NOTE: do i need this?

    $.get("/api/discord/twitchalerts/get", {guild_id: guild_id})
    .done(function (data) {

      $("#alert_amount").text(data.total);

      var AlertList = $("#twitchalert_list").html("");
      for (var alert of data.result) {
        var Template = $("[phantom] .twitchalert").clone();
        var twitch_name = alert.twitch_channel_name ? alert.twitch_channel_name : `Unknown channel name, ID: ${alert.twitch_channel_id}`;
        var discord_channel = DiscordDashboard.getDiscordChannelByID(alert.discord_channel_id);

        Template.find(".discord").text(discord_channel ? "#"+discord_channel.name : "(DELETED CHANNEL)");
        Template.find(".twitch").text(twitch_name);
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

  detail(HTMLRow) {
    var TwitchAlertsO = this;
    var guild_id = $("#guild_id").val();
    var alert_id = $(HTMLRow).attr("alert-id");

    $.get("/api/discord/twitchalerts/get", {guild_id: guild_id, alert_id: alert_id})
    .done(function (data) {

      var alert = data.result.shift();
      console.log(alert);

      insertData("#alert_modal", alert);
      $("#alert_modal").modal("show");
      $("#alert_modal").attr("alert-id", alert.alert_id);
      $("#alert_modal").attr("mode", "edit");

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load twitchalert"} );
    })

  }

});
