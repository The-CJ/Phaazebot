function loginAccount() {

  let data = extractData('#login_space');
  $.post('/api/account/phaaze/login', data).done(function (data) {
    CookieManager.set("phaaze_session", data.phaaze_session, data.expire);
    $("#login_space").addClass("animated zoomOutUp");
    setTimeout(function () {
      window.location = "/account";
    }, 1000);
  }).fail(function (data) {
    $("#login_space [name=phaaze_username]").addClass("animated shake");
    $("#login_space [name=phaaze_password]").addClass("animated shake").val("");
    setTimeout(function () {
      $("#login_space [name=phaaze_username], #login_space [name=phaaze_password]").removeClass("animated shake");
    }, 1000);
    generalAPIErrorHandler( {data:data, msg:"Login failed", color:Display.color_warning} );
  })
}
