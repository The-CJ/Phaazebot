$("document").ready(function () {
  getRoles();
})

function getRoles() {
  $.get("/api/admin/roles/get")
  .done(function (data) {

    var RoleList = $("#role_list").html("");

    for (var role of data.result) {
      var Template = $("[phantom] .role").clone();

      Template.attr("role-id", role.id);
      Template.find(".name").text(role.name);
      Template.find("[can_be_removed]").attr("can_be_removed", role.can_be_removed ? "true" : "false");

      RoleList.append(Template);
    }

  })
  .fail(function (data) {
    let msg = data.responseJSON ? data.responseJSON.error : "unknown";
    Display.showMessage( {content:msg, color:Display.color_critical} );
    console.log(data);
  })
}

function editRole(HTMLElement) {
  var role_id = $(HTMLElement).attr("role-id");

  $.get("/api/admin/roles/get", {role_id: role_id})
  .done(function (data) {

    var role = data.result[0];

    $("#edit_create_role").attr("mode", "edit");
    $("#edit_create_role .modal-title").text("Edit role:");

    $("#edit_create_role").find("[name=id]").val(role.id);
    $("#edit_create_role").find("[name=id]").closest(".row").show();

    $("#edit_create_role").find("[name=name]").val(role.name);
    $("#edit_create_role").find("[name=name]").attr("readonly", true);

    $("#edit_create_role").find("[name=description]").val(role.description);

    $("#edit_create_role").modal("show");
  })

  .fail(function (data) {
    let msg = data.responseJSON ? data.responseJSON.error : "unknown";
    Display.showMessage( {content:msg, color:Display.color_critical} );
    console.log(data);
  });
}

function saveRole() {

  var req = extractData("#edit_create_role[mode=edit]");
  req["role_id"] = req["id"];

  $.post("/api/admin/roles/edit", req)
  .done(function (data) {

    Display.showMessage( {content:data.msg, color:Display.color_success} );
    $("#edit_create_role").modal("hide");

  })

  .fail(function (data) {
    let msg = data.responseJSON ? data.responseJSON.error : "unknown";
    Display.showMessage( {content:msg, color:Display.color_critical} );
    console.log(data);
  });

}
