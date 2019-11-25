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
