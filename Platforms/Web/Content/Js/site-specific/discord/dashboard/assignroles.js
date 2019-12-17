var AssignRoles = new (class {
  constructor() {

  }

  show() {
    var guild_id = $("#guild_id").val();

    $.get("/api/discord/assignroles/get", {guild_id: guild_id})
    .done(function (data) {

      $("#assign_role_amount").text(data.result.length);
      var AssignRoleList = $("#assign_role_list").html("");

      for (var assigerole of data.result) {
        var Template = $("[phantom] .assignrole").clone();
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
    $("#assignrole_create .modal-title").text("New assign role");
    $("#assignrole_create").attr("mode", "create");
    $("#assignrole_create").modal("show");
  }

  detail(HTMLRow) {
    var AssignRolesO = this;
    var guild_id = $("#guild_id").val();
    var assignrole_id = $(HTMLRow).attr("assignrole-id");

    $.get("/api/discord/assignroles/get", {guild_id: guild_id, assignrole_id:assignrole_id})
    .done(function (data) {
      var assignrole = data.result[0];
      insertData("#assignrole_create", assignrole);
      $("#assignrole_create .modal-title").text("Edit assign role");
      $("#assignrole_create").attr("mode", "edit");
      $("#assignrole_create").modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load assign role details"} );
    })
  }

  create() {
    var AssignRoleO = this;
    var req = extractData("#assignrole_create");
    req["guild_id"] = $("#guild_id").val();

    $.get("/api/discord/assignroles/create", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success});
      $("#assignrole_create").modal("hide");
      AssignRoleO.show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not create assign role"} );
    })
  }

  edit() {
    var AssignRoleO = this;
    var req = extractData("#assignrole_create");
    req["guild_id"] = $("#guild_id").val();

    $.get("/api/discord/assignroles/edit", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success});
      $("#assignrole_create").modal("hide");
      AssignRoleO.show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not edit assign role"} );
    })

  }

  delete() {
    var AssignRoleO = this;
    var req = extractData("#assignrole_create");
    req["guild_id"] = $("#guild_id").val();

    if (!confirm("Are you sure you want to delete this assign role?")) { return; }

    $.get("/api/discord/assignroles/delete", req)
    .done(function (data) {
      Display.showMessage({content: data.msg, color:Display.color_success});
      $("#assignrole_create").modal("hide");
      AssignRoleO.show();
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not delete assign role"} );
    })

  }

});
