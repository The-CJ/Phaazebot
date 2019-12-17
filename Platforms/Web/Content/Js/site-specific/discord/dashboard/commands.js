var Commands = new (class {
  constructor() {

  }

  show() {
    var guild_id = $("#guild_id").val();

    $.get("/api/discord/commands/get", {guild_id: guild_id, show_hidden: true})
    .done(function (data) {

      $("#command_amount").text(data.result.length);
      var CommandList = $("#command_list").html("");

      for (var command of data.result) {
        var Template = $("[phantom] .command").clone();
        Template.find(".trigger").text(command.trigger);
        Template.find(".function").text(command.name);
        Template.find(".require").text( discordTranslateRequire(command.require) );
        Template.find(".cost").text(command.cost);
        Template.find(".uses").text(command.uses);
        Template.find(".cooldown").text(command.cooldown);
        Template.attr("command-id", command.command_id);

        if (command.hidden) {
          Template.find(".function").addClass("hidden");
          Template.find(".function").attr("title", "This is a hidden command and can not be viewed via web, without permissions");
        }

        if (!command.active) {
          Template.addClass("non-active");
        }

        CommandList.append(Template);
      }

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"Could not load commands"} );
    })
  }

  createModal() {
    $("#command_create [clear-after-success]").val("");
    $("#command_create [command-setting=simple]").hide();
    $("#command_create [extra-command-setting], #command_create [extra-command-setting] [name=content]").hide();
    $("#command_create .modal-title").text("New Command");
    $("#command_create").attr("mode", "new");
    $("#command_create").modal("show");
  }

  create() {
    var CommandsObj = this;
    var guild_id = $("#guild_id").val();
    var r = {
      "guild_id": guild_id,
      "trigger": $("#command_create [name=trigger]").val(),
      "content": $("#command_create [name=content]").val(),
      "function": $("#command_create [name=function]").val(),
      "complex": $("#command_create [name=commandtype]").val() == "complex" ? true : false,
      "hidden": $("#command_create [name=hidden]").is(":checked"),
      "cooldown": $("#command_create [name=cooldown]").val(),
      "require": $("#command_create [name=require]").val(),
      "required_currency": $("#command_create [name=required_currency]").val()
    };

    $.post("/api/discord/commands/create", r)
    .done(function (data) {
      Display.showMessage({content: "Successfull created command: "+data.command, color:Display.color_success});
      $("#command_create").modal("hide");
      CommandsObj.show();
      // after successfull command, reset modal
      $("#command_create [clear-after-success]").val("");
      $("#command_create [command-setting], #command_create [extra-command-setting]").hide();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"command creation failed"} );
    })

  }

  delete() {
    var CommandsObj = this;
    var r = extractData("#command_create");
    r["guild_id"] = $("#guild_id").val();

    if (!confirm("Are you sure you want to delete the command?")) { return; }

    $.post("/api/discord/commands/delete", r)
    .done(function (data) {
      Display.showMessage({content: "Successfull deleted command: "+data.command, color:Display.color_success});
      $("#command_create").modal("hide");
      CommandsObj.show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"command delete failed"} );
    })
  }

  edit() {
    var CommandsObj = this;
    var guild_id = $("#guild_id").val();
    var r = {
      "guild_id": guild_id,
      "command_id": $("#command_create [name=command_id]").val(),
      "trigger": $("#command_create [name=trigger]").val(),
      "content": $("#command_create [name=content]").val(),
      "function": $("#command_create [name=function]").val(),
      "complex": $("#command_create [name=commandtype]").val() == "complex" ? true : false,
      "hidden": $("#command_create [name=hidden]").is(":checked"),
      "active": $("#command_create [name=active]").is(":checked"),
      "cooldown": $("#command_create [name=cooldown]").val(),
      "require": $("#command_create [name=require]").val(),
      "required_currency": $("#command_create [name=required_currency]").val()
    };

    $.post("/api/discord/commands/edit", r)
    .done(function (data) {
      Display.showMessage({content: "Successfull edited command: "+data.command, color:Display.color_success});
      $("#command_create").modal("hide");
      CommandsObj.show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"command edit failed"} );
    })
  }

  detail(HTMLCommandRow) {
    var CommandsObj = this;
    var guild_id = $("#guild_id").val();
    var command_id = $(HTMLCommandRow).attr("command-id");

    $.get("/api/discord/commands/get", {guild_id: guild_id, command_id:command_id, show_hidden: true})
    .done(function (data) {
      var command = data.result[0];

      insertData("#command_create", command);

      $("#command_create .modal-title").text("Edit command: "+command.trigger);
      $("#command_create [name=required_currency]").val( command.cost );
      $("#command_create [name=cooldown], #command_create [name=cooldown_slider]").val( command.cooldown );
      $("#command_create [name=commandtype]").val( command.complex ? "complex" : "simple" );
      if (command.hidden) { $("#command_create [name=hidden]").prop( "checked", true ); }
      else { $("#command_create [name=hidden]").prop( "checked", false ); }

      if (!command.complex) {
        CommandsObj.loadCommands(null, "simple", command.function);
        CommandsObj.loadCommandInfo(null, command.function);
      }

      $("#command_create [extra-command-setting] [name=content]").val(command.content);
      $("#command_create").attr("mode", "edit");
      $("#command_create").modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load command details"} );
    })
  }

  loadCommands(HTMLSelect, command_type, preselected) {
    $("#command_create [command-setting]").hide();
    var command_type = $(HTMLSelect).val() || command_type;
    if (command_type == "complex") {
      $("[command-setting=complex]").show();
      return;
    }

    if (command_type == "simple") {

      $.get("/api/discord/commands/list")
      .done(function (data) {
        var Options = $("#command_create [name=function]").html("");
        Options.append( $("<option value=''>Choose a function...</option>") );
        for (var cmd of data.result) {
          let Opt = $("<option>");
          Opt.attr("value", cmd.function);
          Opt.text(cmd.name);
          Options.append(Opt);
        }
        if (preselected) { Options.val(preselected); }
        $("[command-setting=simple]").show();
      })
      .fail(function (data) {
        generalAPIErrorHandler( {data:data, msg:"could ould not load command list"} );
      })

    }
  }

  loadCommandInfo(HTMLSelect, preselected) {
    $("#command_create [extra-command-setting], #command_create [extra-command-setting] [name=content]").hide();
    var function_ = $(HTMLSelect).val() || preselected;
    if (isEmpty(function_)) {return;}

    $.get("/api/discord/commands/list", {function: function_})
    .done(function (data) {

      if (data.result.length == 0) {
        return Display.showMessage({content: "Could not find your selected command...", color:Display.color_critical});
      }

      var cmd = data.result[0];

      $("#command_create [extra-command-setting] [name=description]").text(cmd.description);
      $("#command_create [extra-command-setting] [name=details]").text(cmd.details);
      if (cmd.need_content) {
        $("#command_create [extra-command-setting] [name=content]").show();
      }

      $("#command_create [extra-command-setting]").show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load command details"} );
    })
  }
});
