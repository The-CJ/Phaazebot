$("document").ready(function () {
  AdminRole.show();
})

var AdminRole = new (class {
  constructor() {
    this.modal_id = "#role_modal";
    this.list_id = "#role_list";
    this.phantom_class = ".role";
    this.total_field_id = "#role_amount";

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
    var AdminRoleO = this;
    $.get("/api/admin/roles/get", x)
    .done(function (data) {

      AdminRoleO.updatePageIndexButtons(data);

      var RoleList = $(AdminRoleO.list_id).html("");
      $(AdminRoleO.total_field_id).text(data.total);

      for (var role of data.result) {
        var Template = $(`[phantom] ${AdminRoleO.phantom_class}`).clone();

        insertData(Template, role, 0);
        Template.attr("role-id", role.role_id);

        let icon = role.can_be_removed ? `<i class="fas fa-unlock"></i>` : `<i class="fas fa-lock"></i>`;
        Template.find("[name=can_be_removed]").html(icon);

        RoleList.append(Template);
      }

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"can't load roles"} );
    });
  }

  // utils
  nextPage(last=false) {
    this.current_page += 1;
    if (last) { this.current_page = this.current_max_page; }

    var search = extractData("main .controls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  prevPage(first=false) {
    this.current_page -= 1;
    if (first) { this.current_page = 0; }

    var search = extractData("main .controls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  updatePageIndexButtons(data) {
    this.current_limit = data.limit;
    this.current_page = data.offset / data.limit;
    this.current_max_page = (data.total / data.limit);
    this.current_max_page = Math.ceil(this.current_max_page - 1);

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
    $("main .controls [name=limit]").val(this.current_limit);
    $("main .controls .pages .prev").attr("disabled", (this.current_page <= 0) );
    $("main .controls .pages .next").attr("disabled", (this.current_page >= this.current_max_page) );
    $("main .controls .pages .page").text(this.current_page+1);
  }

  setElementState(x={}) {
    if (x.disable_can_be_remove != undefined) {
      $(`${this.modal_id} [name=can_be_removed]`).attr("disabled", x.disable_can_be_remove);
    }

    if (x.readonly_name != undefined) {
      $(`${this.modal_id} [name=name]`).attr("readonly", x.readonly_name);
    }

    if (x.show_delete != undefined) {
      if (x.show_delete) { $(`${this.modal_id} [delete]`).show(); }
      else { $(`${this.modal_id} [delete]`).hide(); }
    }

  }

  // create
  createModal() {
    $(this.modal_id).attr("mode", "create");
    resetInput(this.modal_id);
    this.setElementState( {readonly_name:false, disable_can_be_remove:false, show_delete:false} );
    $(this.modal_id).modal("show");
  }

  create() {
    var AdminRoleO = this;
    var req = extractData(this.modal_id);

    $.post("/api/admin/roles/create", req)
    .done(function (data) {

      Display.showMessage( {content:data.msg, color:Display.color_success} );
      $(AdminRoleO.modal_id).modal("hide");
      AdminRoleO.show();

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"role create failed"} );
    });
  }

  // edit
  editModal(HTMLButton) {
    var AdminRoleO = this;
    var req = {
      "role_id": $(HTMLButton).closest(AdminRoleO.phantom_class).attr("role-id")
    };

    $.get("/api/admin/roles/get", req)
    .done(function (data) {

      var role = data.result.pop();

      $(AdminRoleO.modal_id).attr("mode", "edit");
      insertData(AdminRoleO.modal_id, role);

      var state = {};
      state.readonly_name = !role.can_be_removed;
      state.disable_can_be_remove = !role.can_be_removed;
      state.show_delete = role.can_be_removed;
      AdminRoleO.setElementState(state);
      $(AdminRoleO.modal_id).modal("show");
    })

    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"can't load role"} );
    });
  }

  edit() {
    var AdminRoleO = this;
    var req = extractData(this.modal_id);

    if (!req.can_be_removed) {
      // lets do a cheeky move, when can_be_removed is false and the checkbox is not disabled,
      // means it was not disabled before, we show a warning
      let was_disabled = $(`${AdminRoleO.modal_id} [name=can_be_removed]`).is(":disabled");
      if (!was_disabled) {
        let c = confirm("Setting 'Can be removed' to false will create a permanent role that cant be removed, continue?");
        if (!c) {return;}
      }
    }

    $.post("/api/admin/roles/edit", req)
    .done(function (data) {

      Display.showMessage( {content:data.msg, color:Display.color_success} );
      $(AdminRoleO.modal_id).modal("hide");
      AdminRoleO.show();

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"edit role failed"} );
    });
  }

  // delete
  deleteFromModal() {
    var c = confirm("Are you sure you want to delete this role?");
    if (!c) {return;}

    var role_id = $(this.modal_id).find("[name=role_id]").val();
    this.delete(role_id);
  }

  delete(role_id) {
    var AdminRoleO = this;
    var req = {role_id:role_id};

    $.post("/api/admin/roles/delete", req)
    .done(function (data) {

      Display.showMessage( {content:data.msg, color:Display.color_success} );
      $(AdminRoleO.modal_id).modal("hide");
      AdminRoleO.show();

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"role delete failed"} );
    });
  }
})
