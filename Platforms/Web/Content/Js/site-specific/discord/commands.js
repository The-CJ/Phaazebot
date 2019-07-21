$("document").ready(function () {
  loadCommands();
})

function loadCommands() {

  var guild_id = $("#guild_id").val();

  $.get("/api/discord/commands/get", {guild_id: guild_id})
  .done(function (data) {
    console.log(data);
  })
  .fail(function (data) {
    Display.showMessage({content: "Could not load commands...", color:Display.color_critical});
    console.log(data);
  })

}
