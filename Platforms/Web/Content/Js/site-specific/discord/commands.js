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
      Template.find(".description").text(command.description ? command.description : "");
      Template.find(".require").text( translateRequire(command.require) );
      Template.find(".cost").text(command.cost);
      Template.find(".uses").text(command.uses);
      Template.attr("command-id", command.id);

      if (command.hidden) {
        Template.find(".description").addClass("hidden");
        Template.find(".description").attr("title", "Execute the command in the Discord server to see the result.");
      }

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

function detailCommand(HTMLCommand) {

  HTMLCommand = $(HTMLCommand);

  var guild_id = $("#guild_id").val();
  var command_id = HTMLCommand.attr("command-id");

  $.get("/api/discord/commands/get", {guild_id: guild_id, command_id:command_id})
  .done(function (data) {
    var command = data.result[0];
    var currency = command.cost == 1 ? $("#guild_currency").val() : $("#guild_currency_multi").val();
    console.log(command);
    $("#command_detail [name=trigger]").text(command.trigger);
    $("#command_detail [name=require]").text( translateRequire(command.require) );
    $("#command_detail [name=uses]").text( command.uses + " times" );
    $("#command_detail [name=cost]").text( command.cost + " " + currency );


    $("#command_detail").modal("show");
  })
  .fail(function (data) {
    Display.showMessage({content: "Could not load command detail...", color:Display.color_critical});
    console.log(data);
  })

}
