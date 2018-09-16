function create_account() {
  let data = extract_data($('#register_space'));
  $.post('/api/account/create', data).done(function (data) {
    console.log(data);
  }).fail(function (data) {
    data = data.responseJSON;
    console.log(data);
  })
}