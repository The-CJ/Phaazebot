function submit_login() {
  var login = $("#loginname").val();
  var password = $("#password").val();

  var r = {};

  r["login"] = login;
  r["password"] = password;

  $.post("/api/db/login", JSON.stringify(r))
  .done(
    function (data) {
      $('#loginname').addClass("animated bounceOutLeft");
      $('#password').addClass("animated bounceOutRight");
      $('#sub_button').addClass("animated flipOutX");
      setTimeout(function () {
        document.cookie = "fileserver_session="+data.fileserver_session+"; Path=\"/\"";
        location.reload();
      },1000);
    }
  )
  .fail(
    function (data) {
      if (data.responseJSON.error == 'missing_data') {
        $('#loginname').addClass("animated pulse");
        $('#password').addClass("animated pulse");
        setTimeout(function () {
          $('#loginname').removeClass("animated pulse");
          $('#password').removeClass("animated pulse");
        },1000);
        return ;
      }
      if (data.responseJSON.error == "wrong_data") {
        $('#loginname').addClass("animated shake");
        $('#password').addClass("animated shake");
        $('#sys_msg').text("Password or Login Name not found.");
        $('#password').val("");
        setTimeout(function () {
          $('#loginname').removeClass("animated shake");
          $('#password').removeClass("animated shake");
        },1000);
        return ;
      }
    }
  );
}
