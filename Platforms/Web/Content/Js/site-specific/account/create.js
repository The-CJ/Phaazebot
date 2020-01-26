function createAccount() {

  let data = extractData('#register_space');

  $.post('/api/account/phaaze/create', data).done(function (data) {
    window.location = "/account/login?new";
  }).fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"Creation failed", color:Display.color_warning} );
  })
}
