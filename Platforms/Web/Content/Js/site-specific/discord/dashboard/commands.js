var Commands = new (class {
  constructor() {
    this.modal_id = "#command_create";
    this.list_id = "#command_list";
    this.amount_field_id = "#command_amount";
    this.phantom_class = ".command";
  }

  show() {
    var CommandsO = this;
    var guild_id = $("#guild_id").val();

    $.get("/api/discord/commands/get", {guild_id: guild_id, show_hidden: true})
    .done(function (data) {

      $(CommandsO.amount_field_id).text(data.result.length);
      var CommandList = $(CommandsO.list_id).html("");

      for (var command of data.result) {
        var Template = $(`[phantom] ${CommandsO.phantom_class}`).clone();
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
    $(`${this.modal_id} input, ${this.modal_id} textarea`).val("");
    $(`${this.modal_id} [command-setting]`).hide();
    $(`${this.modal_id} [extra-command-setting], ${this.modal_id} [extra-command-setting] [name=content]`).hide();
    $(`${this.modal_id} .modal-title`).text("New Command");
    $(this.modal_id).attr("mode", "new");
    $(this.modal_id).modal("show");
  }

  create() {
    var CommandsO = this;
    var req = extractData(this.modal_id);
    req["complex"] = $(`${this.modal_id} [name=commandtype]`).val() == "complex" ? true : false,
    req["guild_id"] = $("#guild_id").val();

    $.post("/api/discord/commands/create", req)
    .done(function (data) {
      Display.showMessage({content: "Successfull created command: "+data.command, color:Display.color_success});
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

  delete() {
    var CommandsO = this;
    var req = extractData(this.modal_id);
    req["guild_id"] = $("#guild_id").val();

    if (!confirm("Are you sure you want to delete the command?")) { return; }

    $.post("/api/discord/commands/delete", req)
    .done(function (data) {
      Display.showMessage({content: "Successfull deleted command: "+data.command, color:Display.color_success});
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
      Display.showMessage({content: "Successfull edited command: "+data.command, color:Display.color_success});
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
