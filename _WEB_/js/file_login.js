function submit_login() {
  var login = $("#loginname").val();
  var password = $("#password").val();

  var r = {};

  r["login"] = login;
  r["password"] = password;

  $.post("?login", JSON.stringify(r), function (data) {
    data = JSON.parse(data);
    if (data.error == "missing_data") {
      $('#loginname').css("border","2px solid red");
      $('#loginname').css("background-color","#ffbdbd");
      $('#password').css("border","2px solid red");
      $('#password').css("background-color","#ffbdbd");
      return ;
    }
    document.cookie = "fileserver_session="+data.fileserver_session+";";
    location.reload();
  })

}