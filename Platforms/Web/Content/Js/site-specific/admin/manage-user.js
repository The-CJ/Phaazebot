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

function getUser() {
  $.get("/api/admin/users/get")
  .done(function (data) {

    var UserList = $("#user_list").html("");

    for (var user of data.result) {
      var Template = $("[phantom] .user").clone();

      Template.attr("user-id", user.user_id);
      Template.find(".id").text(user.user_id);
      Template.find(".name").text(user.username);

      UserList.append(Template);
    }

  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"can't load users"} );
  })
}

function detailUser(HTMLElement) {
  var user_id = $(HTMLElement).attr("user-id");

  $.get("/api/admin/users/get", {user_id:user_id})
  .done(function (data) {
    data = data.result.shift();

    $("#edit_create_user .modal-title").text("Edit user: "+data.username);
    $("#edit_create_user").attr("mode", "edit");

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
