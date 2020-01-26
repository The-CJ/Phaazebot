function showPasswordFields() {
  $("[new_password_space] > button").hide();
  $("[new_password_space] > div").show();
}

function saveAccountInfos() {
  var data = extractData("#manage_field");
  var real_data = {};
  for (var d in data) {
    real_data["phaaze_"+d] = data[d];
  }
  $.post("/api/account/phaaze/edit", real_data)
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
    var role_field = $("#role_field").html("");
    for (role of data.user.roles) {
      let r = $("<div class='role'>");
      r.text(role);
      role_field.append(r);
    }
    if (!data.user.roles.length) {
      let r = $("<div class='role none'>(None)</div>");
      role_field.append(r);
    }
  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"Could not load account infomations"} );
  })
}

$("document").ready(
  getAccountInfos
)
