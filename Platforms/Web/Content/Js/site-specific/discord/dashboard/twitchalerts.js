var TwitchAlerts = new (class {
  constructor() {

  }

  show(x={}) {
    var TwitchAlertsO = this;
    var guild_id = $("#guild_id").val();
    // var offset = x["offset"] ? x["offset"] : 0; // NOTE: do i need this?

    $.get("/api/discord/twitchalerts/get", {guild_id: guild_id})
    .done(function (data) {

      console.log(data);

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load twitchalerts"} );
    })
  }

});
