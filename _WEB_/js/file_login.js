function submit_login() {
  var login = $("#loginname").val();
  var password = $("#password").val();

  var r = {};

  r["login"] = login;
  r["password"] = password;

  $.post("/api/db/login", JSON.stringify(r), function (data) {
    data = JSON.parse(data);
    if (data.error == "missing_data") {
      $('#loginname').css("border","2px solid red");
      $('#loginname').css("background-color","#ffbdbd");
      $('#password').css("border","2px solid red");
      $('#password').css("background-color","#ffbdbd");
      return ;
    }
    if (data.error == "wrong_data") {
      $('#loginname').css("border","2px solid red");
      $('#loginname').css("background-color","#ffbdbd");
      $('#password').css("border","2px solid red");
      $('#password').css("background-color","#ffbdbd");
      $('#password').val("");
      $('#sys_msg').text("Password or Login Name not found.");
      return ;
    }
    document.cookie = "fileserver_session="+data.fileserver_session+"; Path=\"/\"";
    location.reload();
  })

}