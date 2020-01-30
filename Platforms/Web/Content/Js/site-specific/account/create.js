function createAccount() {

  let register = extractData('#register_space');

  $.post('/api/account/phaaze/create', register)
  .done(function (data) {
    window.location = "/account/login";
  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"Creation failed", color:Display.color_warning} );
  })
}
