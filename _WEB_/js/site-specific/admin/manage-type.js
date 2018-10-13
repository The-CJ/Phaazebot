function load_role(r) {

  if (r == null) {
    r = {};
  }

  $.get("/api/admin/manage-type/get", r)
  .fail(function (data) {
    m = data.responseJSON ? data.responseJSON.msg : "unknown"
    _show_message(m, "red");
  })
  .done(function (data) {
    let r = $("#result_space").html("");
    roles = data.data
    console.log(roles);
    for (role of roles) {
      let t = $("[tpl] > [role]").clone();
      t.find("[role-id]").attr("role-id", role.id);
      t.find(".role-name").text(role.name);
      t.find(".role-description").text(role.description);
      r.append(t);
    }
  })

}

//

function new_role_modal() {
  $("#new_role").modal("show");
}

function submit_new_role() {
  data = extract_data( $("#new_role") );
  $.post("/api/admin/manage-type/create", data)
  .fail(function (data) {
    m = data.responseJSON ? data.responseJSON.msg : "unknown"
    _show_message(m, "red");
  })
  .done(function (data) {
    _show_message(data.msg, "green");
    $("#new_role").modal("hide");
    load_role();
  })
}

$('document').ready(function () {
  load_role();
})