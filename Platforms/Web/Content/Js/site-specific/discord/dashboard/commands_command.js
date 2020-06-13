var CommandsCommand = new (class {
  constructor() {
    this.modal_id = "#command_modal";
    this.list_id = "#command_list";
    this.total_field_id = "#commands_command_amount";
    this.phantom_class = ".command";
  }

  show() {
    this.load();
  }

  load(x={}) {
    var CommandsCommandO = this;
    x["guild_id"] = $("#guild_id").val();
    x["show_hidden"] = true;

    $.get("/api/discord/commands/get", x)
    .done(function (data) {

      $(CommandsCommandO.total_field_id).text(data.total);
      var EntryList = $(CommandsCommandO.list_id).html("");

      for (var command of data.result) {
        var Template = $(`[phantom] ${CommandsCommandO.phantom_class}`).clone();
        command.require = discordTranslateRequire(command.require);
        insertData(Template, command);
        Template.attr("command-id", command.command_id);

        if (command.hidden) {
          Template.addClass("hidden");
          Template.attr("title", "This is a hidden command and can not be viewed via web, without permissions");
        }

        if (!command.active) {
          Template.addClass("non-active");
        }

        EntryList.append(Template);
      }

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"Could not load commands"} );
    })

}

  // utils
  updateCooldownValues(value) {
    $(this.modal_id).find("[name=cooldown], [name=cooldown_slider]").val(value);
  }

  // create
  createModal() {
    resetInput(this.modal_id);
    $(this.modal_id).attr("mode", "create");
    $(this.modal_id).modal("show");
  }

  create() {
    var CommandsO = this;
    var req = extractData(this.modal_id);
    req["complex"] = $(`${this.modal_id} [name=commandtype]`).val() == "complex" ? true : false,
    req["guild_id"] = $("#guild_id").val();

    $.post("/api/discord/commands/create", req)
    .done(function (data) {
      Display.showMessage({content: "Successfull created command", color:Display.color_success});
      $(CommandsO.modal_id).modal("hide");
      CommandsO.show();
      // after successfull command, reset modal
      $(`${CommandsO.modal_id} input, ${CommandsO.modal_id} textarea`).val("");
      $(`${CommandsO.modal_id} [command-setting], ${CommandsO.modal_id} [extra-command-setting]`).hide();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"command creation failed"} );
    })

  }

  // edit

  // delete

  delete() {
    var CommandsO = this;
    var req = extractData(this.modal_id);
    req["guild_id"] = $("#guild_id").val();

    if (!confirm("Are you sure you want to delete the command?")) { return; }

    $.post("/api/discord/commands/delete", req)
    .done(function (data) {
      Display.showMessage({content: "Successfull deleted command", color:Display.color_success});
      $(CommandsO.modal_id).modal("hide");
      CommandsO.show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"command delete failed"} );
    })
  }

  edit() {
    var CommandsO = this;
    var req = extractData(this.modal_id);
    req["complex"] = $(`${this.modal_id} [name=commandtype]`).val() == "complex" ? true : false,
    req["guild_id"] = $("#guild_id").val();

    $.post("/api/discord/commands/edit", req)
    .done(function (data) {
      Display.showMessage({content: "Successfull edited command", color:Display.color_success});
      $(CommandsO.modal_id).modal("hide");
      CommandsO.show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"command edit failed"} );
    })
  }

  detail(HTMLCommandRow) {
    var CommandsO = this;
    var guild_id = $("#guild_id").val();
    var command_id = $(HTMLCommandRow).attr("command-id");

    $.get("/api/discord/commands/get", {guild_id: guild_id, command_id:command_id, show_hidden: true})
    .done(function (data) {
      var command = data.result[0];

      insertData(CommandsO.modal_id, command);

      $(`${CommandsO.modal_id} .modal-title`).text("Edit command: "+command.trigger);
      $(`${CommandsO.modal_id} [name=required_currency]`).val( command.cost );
      $(`${CommandsO.modal_id} [name=cooldown], ${CommandsO.modal_id} [name=cooldown_slider]`).val( command.cooldown );
      $(`${CommandsO.modal_id} [name=commandtype]`).val( command.complex ? "complex" : "simple" );

      if (!command.complex) {
        CommandsO.loadCommands(null, "simple", command.function);
        CommandsO.loadCommandInfo(null, command.function);
      }

      $(`${CommandsO.modal_id} [extra-command-setting] [name=content]`).val(command.content);
      $(CommandsO.modal_id).attr("mode", "edit");
      $(CommandsO.modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load command details"} );
    })
  }

  loadCommands(HTMLSelect, command_type, preselected) {
    var CommandsO = this;
    $(`${this.modal_id} [command-setting]`).hide();
    var command_type = $(HTMLSelect).val() || command_type;
    if (command_type == "complex") {
      $(`${this.modal_id} [command-setting=complex]`).show();
      return;
    }

    if (command_type == "simple") {

      $.get("/api/discord/commands/list")
      .done(function (data) {
        var Options = $(`${CommandsO.modal_id} [name=function]`).html("");
        Options.append( $("<option value=''>Choose a function...</option>") );
        for (var cmd of data.result) {
          let Opt = $("<option>");
          Opt.attr("value", cmd.function);
          Opt.text(cmd.name);
          Options.append(Opt);
        }
        if (preselected) { Options.val(preselected); }
        $(`${CommandsO.modal_id} [command-setting=simple]`).show();
      })
      .fail(function (data) {
        generalAPIErrorHandler( {data:data, msg:"could ould not load command list"} );
      })

    }
  }

  loadCommandInfo(HTMLSelect, preselected) {
    var CommandsO = this;
    $(`${this.modal_id} [extra-command-setting], ${this.modal_id} [extra-command-setting] [name=content]`).hide();
    var function_ = $(HTMLSelect).val() || preselected;
    if (isEmpty(function_)) {return;}

    $.get("/api/discord/commands/list", {function: function_})
    .done(function (data) {

      if (data.result.length == 0) {
        return Display.showMessage({content: "Could not find your selected command...", color:Display.color_critical});
      }

      var cmd = data.result[0];

      $(`${CommandsO.modal_id} [extra-command-setting] [name=description]`).text(cmd.description);
      $(`${CommandsO.modal_id} [extra-command-setting] [name=details]`).text(cmd.details);
      if (cmd.need_content) {
        $(`${CommandsO.modal_id} [extra-command-setting] [name=content]`).show();
      }

      $(`${CommandsO.modal_id} [extra-command-setting]`).show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load command details"} );
    })
  }

  // utils
  updateSlider(value) {
    $(`${this.modal_id} [name=cooldown_slider]`).val(value);
    $(`${this.modal_id} [name=cooldown]`).val(value);
  }
});