$("document").ready(function () {
  getUser();
  loadUserRoles();
});

function loadUserRoles() {
  $.get("/api/admin/roles/get")
  .done(function (data) {
    var RoleList = $("#new_user_role").html("<option value='0'>(Select role to add)</option>");

    for (var role of data.result) {
      var Opt = $("<option>");

      Opt.text(role.name);
      Opt.attr("value", role.role_id);

      RoleList.append(Opt);
    }
  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"can't load roles"} );
  })

}

// user
function getUser() {
  $.get("/api/admin/users/get")
  .done(function (data) {

    var UserList = $("#user_list").html("");

    for (var user of data.result) {
      var Template = $("[phantom] .user").clone();

      Template.attr("user-id", user.user_id);
      Template.find(".name").text(user.username);

      UserList.append(Template);
    }

  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"can't load users"} );
  })
}

function detailUser(HTMLElement, overwrite_user_id) {
  var user_id;
  if (HTMLElement) {
    var user_id = $(HTMLElement).attr("user-id");
  } else {
    user_id = overwrite_user_id;
  }


  $.get("/api/admin/users/get", {user_id:user_id})
  .done(function (data) {
    data = data.result.shift();

    $("#edit_create_user .modal-title").text("Edit user: "+data.username);
    $("#edit_create_user").attr("mode", "edit");
    $("#edit_create_user [name=password]").val("");

    insertData("#edit_create_user", data, true);
    var RoleList = $("#user_role_list").html("");
    for (var role of data.roles) {
      var RoleTemplate = $("[phantom] .role").clone();
      RoleTemplate.find(".name").text(role);
      RoleList.append(RoleTemplate);
    }

    $("#edit_create_user").modal("show");
  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"can't load user"} );
  })
}

function editUser() {
  var req = extractData("#edit_create_user");
  $.post("/api/admin/users/edit", req)
  .done(function (data) {

    Display.showMessage( {content:data.msg, color:Display.color_success} );
    $("#edit_create_user").modal("hide");
    getUser();

  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"can't edit user roles"} );
  })
}

function showCreate() {
  resetInput("#edit_create_user");
  $("#edit_create_user .modal-title").text("Create new user");
  $("#edit_create_user").attr("mode", "create");
  $("#edit_create_user").modal("show");
}

function createUser() {

  var req = extractData("#edit_create_user");
  $.post("/api/admin/users/create", req)
  .done(function (data) {

    Display.showMessage( {content:data.msg, color:Display.color_success} );
    $("#edit_create_user").modal("hide");
    getUser();

  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"can't create user"} );
  })

}

function deleteUser() {
  var req = extractData("#edit_create_user");

  var c = confirm(`Sure you want to delete user:\n'${req["username"]}' [ID:${req["user_id"]}]`);
  if (!c) { return; }

  $.post("/api/admin/users/delete", req)
  .done(function (data) {

    Display.showMessage( {content:data.msg, color:Display.color_success} );
    $("#edit_create_user").modal("hide");
    getUser();

  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"can't delete user"} );
  });

}

// user roles
function addUserRole() {
  var user_id = $("#edit_create_user [name=user_id]").val();
  var role_id = $("#new_user_role").val();
  var req = {
    user_id: user_id,
    userrole_action: "add",
    userrole_role: role_id,
  };
  $.post("/api/admin/users/edit", req)
  .done(function (data) {

    Display.showMessage( {content:data.msg, color:Display.color_success} );
    detailUser(null, user_id)

  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"can't edit user roles"} );
  })
}

function removeUserRole(HTMLButton) {
  HTMLButton = $(HTMLButton);
  var role_name = HTMLButton.closest(".role").find(".name").text();
  var user_id = HTMLButton.closest(".modal").find("[name=user_id]").val();

  var req = {
    user_id: user_id,
    userrole_action: "remove",
    userrole_role: role_name,
  };

  $.post("/api/admin/users/edit", req)
  .done(function (data) {

    Display.showMessage( {content:data.msg, color:Display.color_success} );
    detailUser(null, user_id)

  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"can't edit user roles"} );
  })
}
