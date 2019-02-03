function save_wiki() {
  r = extract_data($("div[edit_table]"));

  $.post("/api/wiki/save", r)
  .fail(function (data) {
    m = data.responseJSON ? data.responseJSON.msg : "unknown";
    _show_message(m, "red");
  })
  .done(function (data) {
    var bbb = $("[name=url_id]").val();
    window.location = "/wiki/"+bbb;
  })
}