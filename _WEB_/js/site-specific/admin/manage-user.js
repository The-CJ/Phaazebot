function load_user(r) {

  if (r == null) {
    r = {};
  }

  $.get("/api/admin/manage-user/get", r)
  .fail(function (data) {
    m = data.responseJSON ? data.responseJSON.msg : "unknown"
    _show_message(m, "red");
  })
  .done(function (data) {
    let r = $("#result_space").html("");
    for (user of data) {
      let t = $("[tpl] > [user]").clone();
      t.find("[user-id]").attr("user-id", user.id);
      t.find(".user-name").text(user.username);
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

function manage_roles(b) {

  let user_id = b.closest("[user]").find(".user-entry").attr("user-id");
  let r = {"userid":user_id, "detail":1};
  $.get("/api/admin/manage-user/get", r)
  .fail(function (data) {
    m = data.responseJSON ? data.responseJSON.msg : "unknown"
    _show_message(m, "red");
  })
  .done(function (user) {
    $.get("/api/admin/manage-type/get")
    .fail(function (data) {
      m = data.responseJSON ? data.responseJSON.msg : "unknown"
      _show_message(m, "red");
    })
    .done(function (role) {

      user = user[0];

      $("#role_manager").find('.role-user').text(user.username);
      $("#role_manager").find('[name=user-id]').val(user.id);

      var modal_body = $("#role_manager .modal-body").html("");
      for (r of role) {
        var role_tpl = $('#role_manager > [role-tpl]').clone().attr('hidden', false);

        role_tpl.attr("role-id" ,r.id);
        role_tpl.find(".role-name").text(r.name);
        role_tpl.find(".role-description").text(r.description);
        role_tpl.find(".role-description").attr("title", r.description);
        if (user.role.indexOf(r.id) > -1) {
          role_tpl.find(".role-active").prop('checked', true);
        }
        modal_body.append(role_tpl);
      }

    });
  });





  $("#role_manager").modal("show");
}

function submit_managed_roles() {
  var new_roles = [];
  let rs = $("#role_manager .modal-body > .manage-role-entry");
  for (check_role of rs) {
    check_role = $(check_role);
    let rid = check_role.attr("role-id");
    let status = check_role.find('[name=active]');
    if (status.prop('checked')) {
        new_roles.push(parseInt(rid));
    }
  }

  var user_id = $("#role_manager [name=user-id]").val();
  var r = {"user_id": user_id, "role": new_roles};
  $.post("/api/admin/manage-user/update", JSON.stringify(r))
  .fail(function (data) {
    m = data.responseJSON ? data.responseJSON.msg : "unknown"
    _show_message(m, "red");
  })
  .done(function (data) {
    _show_message("User successfull updated", "green");
  })
}

function reset_password() {
  alert("TODO: reset_password()");
}

function impersonate(b) {
  b = $(b).closest("[user]").find(".user-entry");
  let user_id = b.attr("user-id");
  var c = confirm("Sure you wanna switch your session to this user?\nCould lead to missing permissions.");

  if (!c) { return }
  $.post("/api/admin/manage-user/impersonate", {'user_id': user_id}).then(function (data) {
    console.log(data);
  })
}

function detail_user(b) {

  b = $(b);
  let iso = b.attr("is-open");
  if (iso == "1") {
    b.siblings().collapse('hide');
    b.attr("is-open", "0");
    return;
  }

  $("#result_space .collapse").collapse("hide");
  $("#result_space [is-open]").attr("is-open", "0");

  let user_id = b.attr("user-id");
  let r = {"userid":user_id, "detail":1};
  $.get("/api/admin/manage-user/get", r)
  .fail(function (data) {
    m = data.responseJSON ? data.responseJSON.msg : "unknown"
    _show_message(m, "red");
  })
  .done(function (data) {
    let d = b.closest("[user]").find(".user-info");
    insert_data(d, data[0]);
    b.attr("is-open", "1");
    b.siblings().collapse('show');
  })

}

$('document').ready(function () {
  load_user();
})