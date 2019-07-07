function showPasswordFields() {
  $("[new_password_space] > button").hide();
  $("[new_password_space] > div").show();
}

function getAccountInfos() {
  $.get("/api/account/phaaze/get")
  .done(function (data) {
    insertData("#manage_field", data.user);
    var role_field = $("#role_field");
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
    console.log(data);
    let msg = "Could not load account infomations";
    Display.showMessage({ content: msg, color: Display.color_critical });
  })
}

$("document").ready(
  getAccountInfos
)
