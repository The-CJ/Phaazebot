function loginAccount() {

  let data = extractData('#login_space');
  $.post('/api/account/phaaze/login', data).done(function (data) {
    CookieManager.set("phaaze_session", data.phaaze_session, data.expire);
    $("#login_space").addClass("animated zoomOutUp");
    setTimeout(function () {
      window.location = "/account";
    }, 1000);
  }).fail(function (data) {
    $("#login_space [name=username]").addClass("animated shake");
    $("#login_space [name=password]").addClass("animated shake").val("");
    setTimeout(function () {
      $("#login_space [name]").removeClass("animated shake");
    }, 1000);
    generalAPIErrorHandler( {data:data, msg:"Login failed", color:Display.color_warning} );
  })
}
