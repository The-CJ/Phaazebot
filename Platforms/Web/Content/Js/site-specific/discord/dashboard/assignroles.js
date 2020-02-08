var AssignRoles = new (class {
  constructor() {
    this.modal_id = "#assignrole_create";
    this.list_id = "#assign_role_list";
    this.amount_field_id = "#assign_role_amount";
    this.phantom_class = ".assignrole";
  }

  show() {
    var AssignRolesO = this;
    var guild_id = $("#guild_id").val();

    $.get("/api/discord/assignroles/get", {guild_id: guild_id})
    .done(function (data) {

      $(AssignRolesO.amount_field_id).text(data.result.length);
      var AssignRoleList = $(AssignRolesO.list_id).html("");

      for (var assigerole of data.result) {
        var Template = $(`[phantom] ${AssignRolesO.phantom_class}`).clone();
        var role = DiscordDashboard.getDiscordRoleByID(assigerole.role_id);

        var role_name = role ? role.name : "";

        Template.attr("assignrole-id", assigerole.assignrole_id);
        Template.find(".trigger").text(assigerole.trigger);
        if (role_name) {
          Template.find(".name").text( role_name );
        }
        else {
          Template.find(".name").text( "(DELETED ROLE)" );
          Template.find(".name").addClass( "red" );
        }

        AssignRoleList.append(Template);
      }

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"Could not load assign roles"} );
    })
  }

  createModal() {
    $(`${this.modal_id} .modal-title`).text("New assign role");
    $(this.modal_id).attr("mode", "create");
    $(this.modal_id).modal("show");
  }

  detail(HTMLRow) {
    var AssignRolesO = this;
    var guild_id = $("#guild_id").val();
    var assignrole_id = $(HTMLRow).attr("assignrole-id");

    $.get("/api/discord/assignroles/get", {guild_id: guild_id, assignrole_id:assignrole_id})
    .done(function (data) {
      var assignrole = data.result[0];
      insertData(AssignRolesO.modal_id, assignrole);
      $(`${AssignRolesO.modal_id} .modal-title`).text("Edit assign role");
      $(AssignRolesO.modal_id).attr("mode", "edit");
      $(AssignRolesO.modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load assign role details"} );
    })
  }

  create() {
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

  edit() {
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

  delete() {
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
