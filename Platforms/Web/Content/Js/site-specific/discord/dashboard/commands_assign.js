var CommandsAssign = new (class {
  constructor() {
    this.modal_id = "#assignrole_modal";
    this.list_id = "#assign_role_list";
    this.total_field_id = "#assign_role_amount";
    this.phantom_class = ".assignrole";

    this.default_limit = 50;
    this.default_page = 0;

    this.current_limit = 0;
    this.current_page = 0;
    this.current_max_page = 0;
  }

  show() {
    // loads in default values or taken from url
    let limit = DynamicURL.get("commands_assign[limit]") || this.default_limit;
    let page = DynamicURL.get("commands_assign[page]") || this.default_page;

    var req = {
      limit: limit,
      offset: (page * limit)
    };

    this.load( req );
  }

  load(x={}) {
    var CommandsAssignO = this;
    x["guild_id"] = $("#guild_id").val();

    $.get("/api/discord/assignroles/get", x)
    .done(function (data) {
      // update view
      CommandsAssignO.updatePageIndexButtons(data);

      var EntryList = $(CommandsAssignO.list_id).html("");
      $(CommandsAssignO.total_field_id).text(data.total);

      for (var entry of data.result) {
        var Template = $(`[phantom] ${CommandsAssignO.phantom_class}`).clone();

        var role = DiscordDashboard.getDiscordRoleByID(entry.role_id);
        entry.role_name = role ? role.name : "(DELETED CHANNEL)";

        insertData(Template, entry);
        Template.attr("assignrole-id", entry.assignrole_id);

        if (isEmpty(role)) {
          Template.addClass("red");
          Template.attr("title", "This role is deleted on the server and can be deleted here as well without any worries");
        }

        EntryList.append(Template);
      }
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"Could not load assign roles"} );
    })
  }

  // utils
  nextPage(last=false) {
    this.current_page += 1;
    var search = extractData("[location=commands_assign] .controlls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  prevPage(first=false) {
    this.current_page -= 1;
    if (first) { this.current_page = 0; }

    var search = extractData("[location=commands_assign] .controlls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  updatePageIndexButtons(data) {
    this.current_limit = data.limit;
    this.current_page = data.offset / data.limit;
    this.current_max_page = (data.total / data.limit);
    this.current_max_page = parseInt(this.current_max_page)

    // update limit url if needed
    if (this.current_limit != this.default_limit) {
      DynamicURL.set("commands_assign[limit]", this.current_limit);
    } else {
      DynamicURL.set("commands_assign[limit]", null);
    }

    // update page url if needed
    if (this.current_page != this.default_page) {
      DynamicURL.set("commands_assign[page]", this.current_page);
    } else {
      DynamicURL.set("commands_assign[page]", null);
    }

    // update html elements
    $("[location=commands_assign] [name=limit]").val(this.current_limit);
    $("[location=commands_assign] .pages .prev").attr("disabled", (this.current_page <= 0) );
    $("[location=commands_assign] .pages .next").attr("disabled", (this.current_page >= this.current_max_page) );
    $("[location=commands_assign] .pages .page").text(this.current_page+1);
  }

  // create
  createModal() {
    resetInput(this.modal_id);
    $(this.modal_id).attr("mode", "create");
    $(this.modal_id).modal("show");
  }

  create() {}

  // edit
  editModal(HTMLButton) {
    var AssignRolesO = this;
    var req = {
      "guild_id": $("#guild_id").val(),
      "assignrole_id": $(HTMLButton).closest(AssignRolesO.phantom_class).attr("assignrole-id")
    };

    $.get("/api/discord/assignroles/get", req)
    .done(function (data) {
      var entry = data.result.pop();
      insertData(AssignRolesO.modal_id, entry);
      $(AssignRolesO.modal_id).attr("mode", "edit");
      $(AssignRolesO.modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load assign role details"} );
    })
  }

  edit() {}

  // delete
  delete(assignrole_id) {}




  _create() {
    var AssignRolesO = this;
    var req = extractData(this.modal_id);
    req["guild_id"] = $("#guild_id").val();

    $.get("/api/discord/assignroles/create", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success});
      $(AssignRolesO.modal_id).modal("hide");
      AssignRolesO.show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not create assign role"} );
    })
  }

  _edit() {
    var AssignRolesO = this;
    var req = extractData(this.modal_id);
    req["guild_id"] = $("#guild_id").val();

    $.post("/api/discord/assignroles/edit", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success});
      $(AssignRolesO.modal_id).modal("hide");
      AssignRolesO.show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not edit assign role"} );
    })

  }

  _delete() {
    var AssignRolesO = this;
    var req = extractData(this.modal_id);
    req["guild_id"] = $("#guild_id").val();

    if (!confirm("Are you sure you want to delete this assign role?")) { return; }

    $.get("/api/discord/assignroles/delete", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success});
      $(AssignRolesO.modal_id).modal("hide");
      AssignRolesO.show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not delete assign role"} );
    })

  }

});
