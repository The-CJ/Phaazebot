$("document").ready(function () {
  getUser();
});

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
    generalAPIErrorHandler( {data:data, msg:"can't load user"} );
  })
}
