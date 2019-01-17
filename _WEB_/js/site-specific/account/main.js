function load_account() {

  $.get("/api/account/get")
  .done(function (data) {
    $("#username").val(data.username);
    $("#email").val(data.email);
    if (data.img_path != null) {
      $("#avatar").html('<img src="'+data.img_path+'" alt="avatar_'+data.id+'">')
    }
  })
  .fail(function (data) {
    m = data.responseJSON ? data.responseJSON.msg : "unknown";
    _show_message(m, "red");
  })

}

function show_newpassword() {
  $("#pw_btn").hide();
  $("#new_password").closest(".col").show();
  $("#new_password2").closest(".col").show();
}

function show_avatarselect() {

}

function save_changes() {

}

$("document").ready(function () {
  load_account();
})