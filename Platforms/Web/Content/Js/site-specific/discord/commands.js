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
      Template.find(".function").text(command.name ? command.name : "");
      Template.find(".require").text( discordTranslateRequire(command.require) );
      Template.find(".cost").text(command.cost);
      Template.find(".uses").text(command.uses);
      Template.attr("command-id", command.command_id);

      if (command.hidden) {
        Template.find(".function").addClass("hidden");
        Template.find(".function").attr("title", "Execute the command in the Discord server to see the result.");
      }

      $("#command_list").append(Template);
    }

  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"could not load commands"} );
  })

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
    $("#command_detail [name=require]").text( discordTranslateRequire(command.require) );
    $("#command_detail [name=uses]").text( command.uses + " times" );
    $("#command_detail [name=cost]").text( command.cost + " " + currency );
    $("#command_detail [name=name]").text( command.name ? command.name : "(Hidden Command)" );
    $("#command_detail [name=description]").text( command.description ? command.description : "Execute the command in the Discord server to see the result." );


    $("#command_detail").modal("show");
  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"could not load command detail"} );
  })

}
