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

    insertData("#edit_create_user", data);

    console.log(data);
    $("#edit_create_user").modal("show");

  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"can't load user"} );
  })
}
