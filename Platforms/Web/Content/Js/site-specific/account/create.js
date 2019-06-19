function createAccount() {

  let data = extractData('#register_space');

  $.post('/api/account/phaaze/create', data).done(function (data) {
    window.location = "/login?new";
  }).fail(function (data) {
    console.log(data);
    data = data.responseJSON.msg ? data.responseJSON.msg : "unknown";
    Display.showMessage({"content": data, "color": Display.color_warning});
  })
}
