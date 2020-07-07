var CommandsCommand = new (class {
  constructor() {
    this.modal_id = "#command_modal";
    this.list_id = "#command_list";
    this.total_field_id = "#commands_command_amount";
    this.phantom_class = ".command";
    this.commands = [];

    this.default_limit = 50;
    this.default_page = 0;

    this.current_limit = 0;
    this.current_page = 0;
    this.current_max_page = 0;
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
      // update view
      CommandsCommandO.updatePageIndexButtons(data);

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
  nextPage(last=false) {
    this.current_page += 1;
    if (last) { this.current_page = this.current_max_page; }

    var search = extractData("[location=commands_command] .controlls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  prevPage(first=false) {
    this.current_page -= 1;
    if (first) { this.current_page = 0; }

    var search = extractData("[location=commands_command] .controlls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  updatePageIndexButtons(data) {
    this.current_limit = data.limit;
    this.current_page = data.offset / data.limit;
    this.current_max_page = (data.total / data.limit);
    this.current_max_page = Math.ceil(this.current_max_page - 1):

    // update limit url if needed
    if (this.current_limit != this.default_limit) {
      DynamicURL.set("commands_command[limit]", this.current_limit);
    } else {
      DynamicURL.set("commands_command[limit]", null);
    }

    // update page url if needed
    if (this.current_page != this.default_page) {
      DynamicURL.set("commands_command[page]", this.current_page);
    } else {
      DynamicURL.set("commands_command[page]", null);
    }

    // update html elements
    $("[location=commands_command] [name=limit]").val(this.current_limit);
    $("[location=commands_command] .pages .prev").attr("disabled", (this.current_page <= 0) );
    $("[location=commands_command] .pages .next").attr("disabled", (this.current_page >= this.current_max_page) );
    $("[location=commands_command] .pages .page").text(this.current_page+1);
  }

  updateCooldownValues(value) {
    $(this.modal_id).find("[name=cooldown], [name=cooldown_slider]").val(value);
  }

  loadCommands(preselected=null) {
    var CommandsCommandO = this;

    $.get("/api/discord/commands/list")
    .done(function (data) {
      CommandsCommandO.commands = data.result;
      var EntryList = $(`${CommandsCommandO.modal_id} [name=function]`).html("");

      EntryList.append( $("<option value=''>Choose a function...</option>") );
      for (var cmd of data.result) {
        let Opt = $("<option>");
        Opt.attr("value", cmd.function);
        Opt.text(cmd.name);
        EntryList.append(Opt);
      }
      if (preselected) {
        EntryList.val(preselected);
        CommandsCommandO.loadCommandsDetails(null, preselected);
      }
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load command list"} );
    });

  }

  loadCommandsDetails(HTMLSelect, preselected=null) {
    if (!preselected) { preselected = $(HTMLSelect).val(); }

    var cmd = null;
    for (let c of this.commands) {
      if (c["function"] == preselected) { cmd = c; break; }
    }

    if (!cmd) {
      // no command found, hide all
      $(`${this.modal_id} [command-setting=description]`).hide();
      $(`${this.modal_id} [command-setting=content]`).hide();
    } else {
      // command found, insert base info
      $(`${this.modal_id} [name=description]`).text(cmd.description);
      $(`${this.modal_id} [command-setting=description]`).show();

      // content management
      if (cmd.need_content) {
        $(`${this.modal_id} [name=content_management]`).text("This command requires a content");
        $(`${this.modal_id} [command-setting=content]`).show();
      } else if (cmd.allowes_content) {
        $(`${this.modal_id} [name=content_management]`).text("This command supports content");
        $(`${this.modal_id} [command-setting=content]`).show();
      } else {
        $(`${this.modal_id} [command-setting=content]`).hide();
      }
    }
  }

  // create
  createModal() {
    this.loadCommands();
    resetInput(this.modal_id);
    $(`${this.modal_id} [command-setting]`).hide();
    $(this.modal_id).attr("mode", "create");
    $(this.modal_id).modal("show");
  }

  create() {
    var CommandsCommandO = this;
    var req = extractData(this.modal_id);
    req["complex"] = false; // for now everything is a simple command
    req["guild_id"] = $("#guild_id").val();

    $.post("/api/discord/commands/create", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success});
      $(CommandsCommandO.modal_id).modal("hide");
      CommandsCommandO.show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"command creation failed"} );
    })

  }

  // edit
  editModal(HTMLButton) {
    var CommandsCommandO = this;
    var req = {
      "guild_id": $("#guild_id").val(),
      "command_id": $(HTMLButton).closest(CommandsCommandO.phantom_class).attr("command-id"),
      "show_hidden": true
    };

    $.get("/api/discord/commands/get", req)
    .done(function (data) {
      var command = data.result.pop();

      insertData(CommandsCommandO.modal_id, command);
      CommandsCommandO.loadCommands(command.function);
      $(CommandsCommandO.modal_id).attr("mode", "edit");
      $(CommandsCommandO.modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load command details"} );
    })
  }

  edit() {
    var CommandsCommandO = this;

    var req = extractData(CommandsCommandO.modal_id);
    req["guild_id"] = $("#guild_id").val();

    $.post("/api/discord/commands/edit", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success});
      $(CommandsCommandO.modal_id).modal("hide");
      CommandsCommandO.show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not edit command details"} );
    });
  }

  // delete
  deleteFromList(HTMLButton) {
    let command_id = $(HTMLButton).closest(this.phantom_class).attr("command-id");
    this.delete(command_id);
  }

  deleteFromModal() {
    let command_id = $(`${this.modal_id} [name=command_id]`).val();
    this.delete(command_id);
  }

  delete(command_id) {
    var CommandsCommandO = this;
    var req = {
      "guild_id": $("#guild_id").val(),
      "command_id": command_id
    };

    if (!confirm("Are you sure you want to delete the command?")) { return; }

    $.post("/api/discord/commands/delete", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success});
      $(CommandsCommandO.modal_id).modal("hide");
      CommandsCommandO.show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"command delete failed"} );
    });
  }

});
