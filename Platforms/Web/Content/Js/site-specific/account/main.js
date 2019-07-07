function showPasswordFields() {
  $("[new_password_space] > button").hide();
  $("[new_password_space] > div").show();
}

function getAccountInfos() {
  $.get("/api/account/phaaze/get")
  .done(function (data) {
    insertData("main", data.user);
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
