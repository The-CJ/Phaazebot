$("document").ready(function () {
  loadDiscordServers();
})

function loadDiscordServers() {

  $.get("/api/discord/servers")
  .done(function (data) {

  })
  .fail(function (data) {

  })

}
