$("document").ready(function () {
  loadCommands();
})

function loadCommands() {

  var guild_id = $("#guild_id").val();

  $.get("/api/discord/commands/get", {guild_id: guild_id})
  .done(function (data) {

    $("#command_amount").text(data.result.length);

    for (command of data.result) {
      var Template = $("[phantom] .command").clone();
      Template.find(".trigger").text(command.trigger);
      Template.find(".content").text(command.content);
      Template.find(".require").text( translateRequire(command.require) );
      Template.find(".cost").text(command.cost);
      Template.find(".uses").text(command.uses);
      Template.attr("command-id", command.id);

      $("#command_list").append(Template);

    }

  })
  .fail(function (data) {
    Display.showMessage({content: "Could not load commands...", color:Display.color_critical});
    console.log(data);
  })

}

function translateRequire(level) {
  if (level == 0) { return "Everyone"; }
  if (level == 1) { return "Regulars"; }
  if (level == 2) { return "Moderators"; }
  if (level == 3) { return "Server Owner"; }
  if (level >= 4) { return "System"; }
}
