function load_user(r) {

  if (r == null) {
    r = {};
  }

  $.get("/api/admin/manage-user/get", r)
  .fail(function (data) {
    m = data.responseJSON.msg ? data.responseJSON.msg != "" : "unknown"
    _show_message(m, "red");
  })
  .done(function (data) {
    let r = $("#result_space").html("");
    users = data.data
    for (user of users) {
      let t = $("[tpl] > [user]").clone();
      t.find("[user-id]").attr("user-id", user.id);
      t.find(".user-name").text(user.username);
      t.find(".user-type").text(user.type.join(", "));
      t.find(".user-id").text(user.id);
      r.append(t);
    }
  })

}

function filter_user() {
  let x = extract_data($("#user_filter"));
  load_user(x);
}

//

function detail_user(b) {
  $("#result_space .collapse").collapse("hide");
  b = $(b);
  let user_id = b.attr("user-id");
  let r = {"userid":user_id, "detail":1};
  $.get("/api/admin/manage-user/get", r)
  .fail(function (data) {
    m = data.responseJSON.msg ? data.responseJSON.msg != "" : "unknown"
    _show_message(m, "red");
  })
  .done(function (data) {
    let d = b.closest("[user]").find(".user-info");
    insert_data(d, data.data[0]);
    b.siblings().collapse('show');
  })

}
$('document').ready(function () {
  load_user();
})