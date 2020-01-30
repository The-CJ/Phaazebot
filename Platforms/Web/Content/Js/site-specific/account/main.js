function showPasswordFields() {
  $("[new_password_space] > button").hide();
  $("[new_password_space] > div").show();
}

function saveAccountInfos() {
  var edit = extractData("#manage_field");
  $.post("/api/account/phaaze/edit", edit)
  .done(function (data) {
    Display.showMessage({content:data.msg, color:Display.color_success});
    getAccountInfos();
  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"Editing failed"} );
  })
}

function getAccountInfos() {
  $.get("/api/account/phaaze/get")
  .done(function (data) {
    insertData("#manage_field", data.user);
    var RoleList = $("#role_list").html("");
    for (role of data.user.roles) {
      var Role = $("<div class='role'>").text(role);
      RoleList.append(Role);
    }
    if (!data.user.roles.length) {
      var Role = $("<div class='role none'>(None)</div>");
      RoleList.append(Role);
    }
  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"Could not load account infomations"} );
  })
}

$("document").ready(function () {
  getAccountInfos();
})
