var Levels = new(class {
  constructor() {
    this.modal_id = "#level_modal";
    this.list_id = "#level_list";
    this.total_field_id = "#level_amount";
    this.phantom_class = ".level";
    this.medal_list_id = "#medal_list";
    this.medal_phantom_class = ".medal";

    this.default_limit = 50;
    this.default_page = 0;

    this.current_limit = 0;
    this.current_page = 0;
    this.current_max_page = 0;

    // this.current_user_medal = [];
  }

  show() {
    // loads in default values or taken from url
    let limit = DynamicURL.get("levels[limit]") || this.default_limit;
    let page = DynamicURL.get("levels[page]") || this.default_page;

    var req = {
      limit: limit,
      offset: (page * limit)
    };

    this.load( req );
  }

  load(x={}) {
    var LevelO = this;
    x["guild_id"] = $("#guild_id").val();
    x["detailed"] = true;

    $.get("/api/discord/levels/get", x)
    .done(function (data) {

      // update view
      LevelO.updatePageIndexButtons(data);

      var LevelList = $(LevelO.list_id).html("");
      $(LevelO.total_field_id).text(data.total);

      for (var level of data.result) {
        var Template = $(`[phantom] ${LevelO.phantom_class}`).clone();

        // set avatar
        var avatar = discordUserAvatar(level.member_id, level.avatar);
        Template.find("img").attr("src", avatar);

        // extra values
        level.medal_amount = (level.medals.length || 0);

        insertData(Template, level);
        Template.attr("member-id", level.member_id);

        if (level.edited) {
          Template.find(".exp").addClass("red");
          Template.find(".exp").attr("title", "This member got edited, the stats can be wrong");
        }

        LevelList.append(Template);
      }

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load levels"} );
    })
  }

  // utils
  nextPage(last=false) {
    this.current_page += 1;
    var search = extractData("[location=levels] .controlls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  prevPage(first=false) {
    this.current_page -= 1;
    if (first) { this.current_page = 0; }

    var search = extractData("[location=levels] .controlls");
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
      DynamicURL.set("levels[limit]", this.current_limit);
    } else {
      DynamicURL.set("levels[limit]", null);
    }

    // update page url if needed
    if (this.current_page != this.default_page) {
      DynamicURL.set("levels[page]", this.current_page);
    } else {
      DynamicURL.set("levels[page]", null);
    }

    // update html elements
    $("[location=levels] [name=limit]").val(this.current_limit);
    $("[location=levels] .pages .prev").attr("disabled", (this.current_page <= 0) );
    $("[location=levels] .pages .next").attr("disabled", (this.current_page >= this.current_max_page) );
    $("[location=levels] .pages .page").text(this.current_page+1);
  }

  loadinModalMedal(guild_id, member_id) {
    var LevelO = this;
    var req = {
      guild_id: guild_id,
      member_id: member_id
    };
    $.get("/api/discord/levels/medals/get", req)
    .done(function (data) {

      var MedalList = $(LevelO.medal_list_id).html("");
      for (var entry of data.result) {
        var Template = $(`[phantom] ${LevelO.medal_phantom_class}`).clone();
        insertData(Template, entry);
        MedalList.append(Template);
      }

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"Could not load medals"} );
    });
  }

  // create
  createMedal() {
    var LevelO = this;
    var new_medal = $("#new_medal").val();
    if (isEmpty(new_medal)) { return; }

    var req = {
      "guild_id": $("#guild_id").val(),
      "member_id": $(`${this.modal_id} [name=member_id]`).val(),
      "name": new_medal
    };

    $.get("/api/discord/levels/medals/create", req)
    .done(function (data) {

      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      $("#new_medal").val("");
      LevelO.loadinModalMedal(req.guild_id, req.member_id);

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"Could not add new medal"} );
    });
  }

  // edit
  editModal(HTMLButton) {
    var LevelO = this;

    var req = {
      "detailed": true,
      "guild_id": $("#guild_id").val(),
      "member_id": $(HTMLButton).closest(LevelO.phantom_class).attr("member-id")
    };
    $.get("/api/discord/levels/get", req)
    .done(function (data) {

      var level = data.result.pop();

      // extra values
      level.display_rank = (level.rank ? `Rank: #${level.rank}` : "Rank: [N/A]");
      level.display_id = (level.member_id ? `ID: ${level.member_id}` : "ID: [N/A]");

      // set avatar
      var avatar = discordUserAvatar(level.member_id, level.avatar, 128);
      $(`${LevelO.modal_id} img`).attr("src", avatar);

      // if name is [N/A], that could mean the user is not on the server, but phaaze did not catch the event to remove him,
      // in this case the owner has the option to remove this user
      // NOTE: if member name themself "[N/A]" there can be removed even duh there are on the server.
      //       that is a wanted feature since a owner can do this at any time, via a API request
      //       So kids, dont be dumb and call yourself '[N/A]' and delete your avatar or you may get deleted
      if (level["username"] == "[N/A]" && level["avatar"] == null) {
        $(`${LevelO.modal_id} button[name=on_server]`).show();
      } else {
        $(`${LevelO.modal_id} button[name=on_server]`).hide();
      }

      insertData(LevelO.modal_id, level);
      LevelO.loadinModalMedal(level.guild_id, level.member_id);
      $(LevelO.modal_id).modal("show");

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"Could not load level details"} );
    });
  }

  editExp() {
    var c = confirm("Editing the exp will leave a permanent [EDITED] mark, unless resettet to 0, be carefull. Want to continue?");
    if (!c) { return; }

    var new_exp = $(`${this.modal_id} [name=exp]`).val();
    this.edit( {exp: new_exp} );
  }

  editCurrency() {
    var new_currency = $(`${this.modal_id} [name=currency]`).val();
    this.edit( {currency: new_currency} );
  }

  editOnServer() {
    var c = confirm("It seems, this member is not on the server anymore and Phaaze did not catch this.\n"+
      "Do you want to set this member to a inactive state?\n"+
      "(This action can not be undone until the member joins the server again)");
    if (!c) { return; }

    this.edit( {on_server: false} );
  }

  edit(update) {
    update["guild_id"] = $("#guild_id").val();
    update["member_id"] = $(`${this.modal_id} [name=member_id]`).val();

    $.post("/api/discord/levels/edit", update)
    .done(function (data) {

      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error updating levels"} );
    })
  }

  // delete
  deleteMedal(HTMLButton) {
    var LevelO = this;
    var medal_id = $(HTMLButton).closest(this.medal_phantom_class).find("[name=medal_id]").val();

    var req = {
      "guild_id": $("#guild_id").val(),
      "member_id": $(`${this.modal_id} [name=member_id]`).val(),
      "medal_id": medal_id
    };

    $.get("/api/discord/levels/medals/delete", req)
    .done(function (data) {

      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      LevelO.loadinModalMedal(req.guild_id, req.member_id);

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"Could not delete medal"} );
    });
  }

});
