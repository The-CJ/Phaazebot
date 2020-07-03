$("document").ready(function () {
  AdminRole.show();
})

function detailRole(HTMLElement) {
  var role_id = $(HTMLElement).attr("role-id");

  $.get("/api/admin/roles/get", {role_id: role_id})
  .done(function (data) {

    var role = data.result.shift();

    $("#edit_create_role").attr("mode", "edit");
    $("#edit_create_role .modal-title").text("Edit role:");

    insertData("#edit_create_role", role);

    if (!role.can_be_removed) {
      $("#edit_create_role").find("[name=can_be_removed]").attr("disabled", true);
      $("#edit_create_role").find("[name=name]").attr("readonly", true);
      $("#edit_create_role button[remove]").hide();
    } else {
      $("#edit_create_role").find("[name=can_be_removed]").attr("disabled", false);
      $("#edit_create_role").find("[name=name]").attr("readonly", false);
      $("#edit_create_role button[remove]").show();
    }

    $("#edit_create_role").modal("show");
  })

  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"can't load role"} );
  });
}

function editRole() {

  var req = extractData("#edit_create_role[mode=edit]");

  $.post("/api/admin/roles/edit", req)
  .done(function (data) {

    Display.showMessage( {content:data.msg, color:Display.color_success} );
    $("#edit_create_role").modal("hide");
    getRoles();

  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"edit role failed"} );
  });
}

function showCreate() {
  $("#edit_create_role").attr("mode", "create");
  $("#edit_create_role .modal-title").text("Create role:");

  $("#edit_create_role").find("input, textarea").val("");
  $("#edit_create_role").find("[name=name]").attr("readonly", false);
  $("#edit_create_role").find("[name=can_be_removed]").attr("disabled", false);

  $("#edit_create_role").modal("show");
}

function createRole() {

  var req = extractData("#edit_create_role");
  $.post("/api/admin/roles/create", req)
  .done(function (data) {

    Display.showMessage( {content:data.msg, color:Display.color_success} );
    $("#edit_create_role").modal("hide");
    getRoles();

  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"role create failed"} );
  });

}

function removeRole() {
  var req = extractData("#edit_create_role");

  var c = confirm("Sure you want to delete role '"+req["name"]+"'?");
  if (!c) { return; }

  $.post("/api/admin/roles/delete", req)
  .done(function (data) {

    Display.showMessage( {content:data.msg, color:Display.color_success} );
    $("#edit_create_role").modal("hide");
    getRoles();

  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"role delete failed"} );
  });
}

var AdminRole = new (class {
  constructor() {
    this.modal_id = "#";
    this.list_id = "#role_list";
    this.phantom_class = ".role";
  }

  show() {
    let limit = DynamicURL.get("limit") || this.default_limit;
    let page = DynamicURL.get("page") || this.default_page;

    var req = {
      limit: limit,
      offset: (page * limit)
    };

    this.load( req );
  }

  load(x={}) {
    var AdminRoleO = this;
    $.get("/api/admin/roles/get", x)
    .done(function (data) {

      var RoleList = $(AdminRoleO.list_id).html("");

      for (var role of data.result) {
        var Template = $(`[phantom] ${AdminRoleO.phantom_class}`).clone();

        insertData(Template, role, 0);
        Template.attr("role-id", role.role_id);

        let icon = role.can_be_removed ? `<i class="fas fa-unlock"></i>` : `<i class="fas fa-lock"></i>`;
        Template.find("[name=can_be_removed]").html(icon);

        RoleList.append(Template);
      }

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"can't load roles"} );
    });
  }


})
