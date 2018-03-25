function submit_login() {
  var login = $("#admin_loginname").val();
  var password = $("#admin_password").val();

  var r = {};

  r["phaaze_username"] = login;
  r["password"] = password;

  $.post("/api/login", JSON.stringify(r))
  .done(
    function (data) {
      $('#admin_loginname').addClass("animated bounceOutLeft");
      $('#admin_password').addClass("animated bounceOutRight");
      $('#sub_button').addClass("animated flipOutX");
      setTimeout(function () {
        setCookie("phaaze_session", data.phaaze_session);
        location.reload();
      },1000);
    }
  )
  .fail(
    function (data) {
      if (data.responseJSON.error == 'missing_data') {
        $('#admin_loginname').addClass("animated pulse");
        $('#admin_password').addClass("animated pulse");
        setTimeout(function () {
          $('#admin_loginname').removeClass("animated pulse");
          $('#admin_password').removeClass("animated pulse");
        },1000);
        return ;
      }
      if (data.responseJSON.error == "wrong_data") {
        $('#admin_loginname').addClass("animated shake");
        $('#admin_password').addClass("animated shake");
        $('#sys_msg').text("Password or Login Name wrong.");
        $('#admin_password').val("");
        setTimeout(function () {
          $('#admin_loginname').removeClass("animated shake");
          $('#admin_password').removeClass("animated shake");
        },1000);
        return ;
      }
    }
  );
}
