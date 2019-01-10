function save_wiki() {
  r = {}
  r["url_id"] = $("[name=url_id]").val();
  r["title"] = $("[name=title]").val();
  r["tags"] = $("[name=tags]").val();
  r["content"] = $("[name=content]").val();

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