function create_account() {
  let data = extract_data($('#register_space'));
  $.post('/api/account/create', data).done(function (data) {
    window.location = "/login?new";
  }).fail(function (data) {
    data = data.responseJSON ? data.responseJSON.msg : "unknown";
    _show_message(data);
  })
}