function load_account() {

  $.get("/api/account/get")
  .done(function (data) {
    $("#username").val(data.username);
    $("#email").val(data.email);
    if (data.img_path != null) {
      $("#avatar").html('<img src="'+data.img_path+'" alt="avatar_'+data.id+'">')
    }
    var r = $("#roles").html("");
    data.role = data.role ? data.role : [];
    if (data.role.length == 0) { r.append($('<h4 class="role-none"></h4>').text("None")); }
    else {
      for (role of data.role) {
        r.append($('<div class="role"></div>').text(role));
      }
    }
    // TODO: add platforms
    var r = $("#platforms").html("");
    data.linked = data.linked ? data.linked : [];
    if (data.linked.length == 0) { r.append($('<h4 class="role-none"></h4>').text("None")); }
    else {
      for (link of data.linked) {
        r.append($('<div class="role-none"></div>').text(link));
      }
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
  $("#avatar_upload_modal").modal("show");
}

function upload_avatar(operation) {
  var payload = {};
  var path = "/api/account/avatar";

  if (operation == false) { payload["remove"] = "true"; }
  else if (operation == true) {
    var f = $("#avatar_upload_modal [name=avatar]");
    payload["file"] = f[0].files[0];
  }
  else { return }

  function success(data) {
    _show_message("Avatar changed!", "green");
    load_account();
  }

  function fail(data) {
    m = data.msg ? data.msg : "unknown";
    _show_message(m, "red");
  }

  upload_file(payload, path, success, fail);
}

function save_changes() {
  r = {
    "current_password":$("#current_password").val(),
    "new_password":$("#new_password").val(),
    "new_password2":$("#new_password2").val(),
    "email":$("#email").val(),
    "username":$("#username").val()
  }
  $.post("/api/account/edit", r)
  .done(function (data) {
    _show_message(data.msg, "green");
    load_account();
  })
  .fail(function (data) {
    m = data.responseJSON ? data.responseJSON.msg : "unknown";
    _show_message(m, "red");
  })
}

$("document").ready(function () {
  load_account();
})