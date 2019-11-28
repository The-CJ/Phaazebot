$("document").ready(function () {
  getUser();
});

function getUser() {
  $.get("/api/admin/users/get")
  .done(function (data) {

    var UserList = $("#user_list").html("");

    for (var user of data.result) {
      console.log(user);
      // var Template = $("[phantom] .role").clone();

      // Template.attr("role-id", role.id);
      // Template.find(".name").text(role.name);
      // Template.find("[can_be_removed]").attr("can_be_removed", role.can_be_removed ? "true" : "false");

      // RoleList.append(Template);
    }

  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"can't load user"} );
  })
}
