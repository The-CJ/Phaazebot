$("document").ready(function () {
  AdminUser.show();
  loadUserRoles();
});

function loadUserRoles() {
  $.get("/api/admin/roles/get")
  .done(function (data) {
    var RoleList = $("#new_user_role").html("<option value='0'>(Select role to add)</option>");

    for (var role of data.result) {
      var Opt = $("<option>");

      Opt.text(role.name);
      Opt.attr("value", role.role_id);

      RoleList.append(Opt);
    }
  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"can't load roles"} );
  });
}

var AdminUser = new (class {
  constructor() {
    this.modal_id = "#user_modal";
    this.list_id = "#user_list";
    this.total_field_id = "#user_amount";
    this.phantom_class = ".user";
    this.role_list_id = "#user_role_list";
    this.role_phantom_class = ".role";

    this.default_limit = 50;
    this.default_page = 0;

    this.current_limit = 0;
    this.current_page = 0;
    this.current_max_page = 0;
  }

  show() {
    let limit = DynamicURL.get("limit") || this.default_limit;
    let page = DynamicURL.get("page") || this.default_page;

    var req = {
      limit: limit,
      offset: (page * limit)
    };

    this.load( req );
  }

  load(x={}) {
    var AdminUserO = this;

    $.get("/api/admin/users/get", x)
    .done(function (data) {

      AdminUserO.updatePageIndexButtons(data);

      var UserList = $(AdminUserO.list_id).html("");
      $(AdminUserO.total_field_id).text(data.total);

      for (var user of data.result) {
        var Template = $(`[phantom] ${AdminUserO.phantom_class}`).clone();

        Template.attr("user-id", user.user_id);
        insertData(Template, user);

        UserList.append(Template);
      }

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"can't load users"} );
    });
  }

  // utils
  nextPage(last=false) {
    this.current_page += 1;
    var search = extractData("main .controlls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  prevPage(first=false) {
    this.current_page -= 1;
    if (first) { this.current_page = 0; }

    var search = extractData("main .controlls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  updatePageIndexButtons(data) {
    this.current_limit = data.limit;
    this.current_page = data.offset / data.limit;
    this.current_max_page = (data.total / data.limit);
    this.current_max_page = parseInt(this.current_max_page)

    // update limit url if needed
    if (this.current_limit != this.default_limit) {
      DynamicURL.set("limit", this.current_limit);
    } else {
      DynamicURL.set("limit", null);
    }

    // update page url if needed
    if (this.current_page != this.default_page) {
      DynamicURL.set("page", this.current_page);
    } else {
      DynamicURL.set("page", null);
    }

    // update html elements
    $("main .controlls [name=limit]").val(this.current_limit);
    $("main .controlls .pages .prev").attr("disabled", (this.current_page <= 0) );
    $("main .controlls .pages .next").attr("disabled", (this.current_page >= this.current_max_page) );
    $("main .controlls .pages .page").text(this.current_page+1);
  }

  loadRolesForUser(user_id) {
    var AdminUserO = this;
    var req = { "user_id": user_id };

    $.get("/api/admin/roles/get", req)
    .done(function (data) {

      var EntryList = $(AdminUserO.role_list_id).html("");
      for (var entry of data.result) {
        var Template = $(`[phantom] ${AdminUserO.role_phantom_class}`).clone();
        insertData(Template, entry);
        Template.attr("role-id", entry.role_id);
        EntryList.append(Template);
      }

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"can't load user"} );
    })

  }

  // create
  createModal() {
    resetInput(this.modal_id);
    $(this.modal_id).attr("mode", "create");
    $(this.modal_id).modal("show");
  }

  create() {
    var AdminUserO = this;
    var req = extractData(this.modal_id);
    $.post("/api/admin/users/create", req)
    .done(function (data) {

      Display.showMessage( {content:data.msg, color:Display.color_success} );
      $(AdminUserO.modal_id).modal("hide");
      AdminUserO.show();

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"can't create user"} );
    })

  }

  // edit
  editModal(HTMLButton) {
    var AdminUserO = this;
    var req = {
      "user_id": $(HTMLButton).closest(AdminUserO.phantom_class).attr("user-id")
    };

    $.get("/api/admin/users/get", req)
    .done(function (data) {
      var user = data.result.pop();

      $(AdminUserO.modal_id).attr("mode", "edit");

      // reset password field
      user.password = "";

      insertData(AdminUserO.modal_id, user);
      AdminUserO.loadRolesForUser(user.user_id);

      $(AdminUserO.modal_id).modal("show");
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"can't load user"} );
    })
  }

  edit() {
    var AdminUserO = this;
    var req = extractData(this.modal_id);
    if (!isEmpty(req["password"])) {
      var c = confirm("This will reset the users password, this cannot be undone. Are you sure?");
      if (!c) { return; }
    }

    $.post("/api/admin/users/edit", req)
    .done(function (data) {

      Display.showMessage( {content:data.msg, color:Display.color_success} );
      $(AdminUserO.modal_id).modal("hide");
      AdminUserO.show();

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"can't edit user roles"} );
    });
  }

  addRole() {
    var AdminUserO = this;

    var req = {
      "user_id": $(`${AdminUserO.modal_id} [name=user_id]`).val(),
      "role_id": $("#new_user_role").val(),
      "operation": "addrole"
    };
    $.post("/api/admin/users/edit", req)
    .done(function (data) {

      Display.showMessage( {content:data.msg, color:Display.color_success} );
      AdminUserO.loadRolesForUser(req["user_id"]);

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"can't edit user roles"} );
    });
  }

  // delete
  removeRole(HTMLButton) {
    var AdminUserO = this;

    var req = {
      "user_id": $(`${AdminUserO.modal_id} [name=user_id]`).val(),
      "role_id": $(HTMLButton).closest(this.role_phantom_class).attr("role-id"),
      "operation": "removerole"
    };
    $.post("/api/admin/users/edit", req)
    .done(function (data) {

      Display.showMessage( {content:data.msg, color:Display.color_success} );
      AdminUserO.loadRolesForUser(req["user_id"]);

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"can't edit user roles"} );
    });
  }

  deleteFromModal() {
    var AdminUserO = this;

    var c = confirm("Are you sure you want to delete this user?");
    if (!c) {return;}

    var user_id = $(this.modal_id).find("[name=user_id]").val();
    this.delete(user_id);
  }

  delete(user_id) {
    var AdminUserO = this;
    var req = { user_id: user_id };
    $.post("/api/admin/users/delete", req)
    .done(function (data) {

      Display.showMessage( {content:data.msg, color:Display.color_success} );
      $(AdminUserO.modal_id).modal("hide");
      AdminUserO.show();

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"can't edit user roles"} );
    });
  }

});
