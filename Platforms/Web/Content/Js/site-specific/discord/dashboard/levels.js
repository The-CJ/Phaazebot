var Levels = new(class {
  constructor() {
    this.modal_id = "#level_modal_edit";

    this.results_per_page = 50;
    this.offset = 0;
    this.total = 0;
    this.current_user_medal = [];
  }

  show(x={}) {
    var LevelO = this;
    var guild_id = $("#guild_id").val();

    x["offset"] = x["offset"] ? x["offset"] : 0;
    x["guild_id"] = guild_id;
    x["detailed"] = true;
    x["limit"] = this.results_per_page;
    x["nickname"] = $("#search [name=nickname]").val();
    x["name_contains"] = $("#search [name=name_contains]").val();
    x["edited"] = $("#search [name=edited]:checked").val();

    $.get("/api/discord/levels/get", x)
    .done(function (data) {

      // store a copy of the current number of entrys
      LevelO.total = data.total;
      LevelO.offset = data.offset;
      LevelO.updatePageIndexButtons();

      var LevelList = $("#level_list").html("");

      for (var level of data.result) {
        var Template = $("[phantom] .level").clone();
        var avatar = discordUserAvatar(level.member_id, level.avatar);

        Template.find(".rank").text(level.rank);
        Template.find(".lvl").text(level.level);
        Template.find(".exp").text(level.exp);
        Template.find(".currency").text(level.currency);
        Template.find(".name").text( level.username );
        Template.find(".avatar").attr("src", avatar);
        Template.find(".medals").text(level.medals.length);
        Template.attr("member-id", level.member_id);

        if (level.edited) {
          Template.find(".exp").addClass("edited");
          Template.find(".exp").attr("title", "This member got edited, the stats can be wrong");
        }

        LevelList.append(Template);
      }

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load levels"} );
    })
  }

  prevPage(first) {
    if (first) {
      this.offset = 0;
    } else {
      this.offset -= (this.results_per_page);
    }
    this.show({offset:this.offset});
  }

  nextPage(last) {
    if (last) {
      this.offset = parseInt(this.total / this.results_per_page) * this.results_per_page;
    } else {
      this.offset += (this.results_per_page);
    }
    this.show({offset:this.offset});
  }

  updatePageIndexButtons() {
    var current_page = (this.offset / this.results_per_page) + 1;
    var max_pages = parseInt((this.total / this.results_per_page) + 1)

    $("#level_pages .index").text(current_page);

    // no more prev pages
    if (current_page <= 1) {
      $("#level_pages .prev").attr("disabled", true);
    } else {
      $("#level_pages .prev").attr("disabled", false);
    }

    // no more next pages
    if (current_page >= max_pages) {
      $("#level_pages .next").attr("disabled", true);
    } else {
      $("#level_pages .next").attr("disabled", false);
    }

  }

  detail(HTMLCommandRow) {
    var LevelO = this;
    var guild_id = $("#guild_id").val();
    var member_id = $(HTMLCommandRow).attr("member-id");
    $.get("/api/discord/levels/get", {guild_id: guild_id, member_id:member_id, detailed: true})
    .done(function (data) {
      var level = data.result[0];

      // set avatar
      var avatar = discordUserAvatar(level.member_id, level.avatar, 128);
      $(`${LevelO.modal_id} img`).attr("src", avatar);

      // insert medals
      LevelO.current_user_medal = level.medals;
      LevelO.buildDetailMedal(LevelO.current_user_medal);

      // edited?
      $(`${LevelO.modal_id} [name=exp]`).attr("edited", level.edited ? "true" : "false");

      // better format, aka lazy format
      level["display_rank"] = (level["rank"] ? "Rank: #"+level["rank"] : "Rank: [N/A]");
      level["display_id"] = (level["rank"] ? "ID: "+level["member_id"] : "ID: [N/A]");

      // if name is [N/A], that could mean the user is not on the server, but phaaze did not catch the event to remove him,
      // in this case the owner has the option to remove this user
      // NOTE: if member name themself "[N/A]" there can be removed even duh there are on the server.
      //       that is a wanted feature since a owner can do this at any time, via a API request
      //       So kids, dont be dumb and call yourself '[N/A]' and delete your avatar or you may get deleted
      if (level["username"] == "[N/A]" && level["avatar"] == null) {
        $(`${LevelO.modal_id} [name=on_server]`).show();
      } else {
        $(`${LevelO.modal_id} [name=on_server]`).hide();
      }

      insertData(LevelO.modal_id, level);

      $(LevelO.modal_id).attr("edit-member", level.member_id);
      $(LevelO.modal_id).modal("show");
      DynamicURL.set("level_member_id", level.member_id);
    })
    .fail(function (data) {
      Display.showMessage({content: "Could not load level details...", color:Display.color_critical});
      console.log(data);
    })
  }

  buildDetailMedal(medal_list) {
    var EntryList = $(`${this.modal_id} .medallist`).html("");
    for (var entry of medal_list) {
      var EntryRow = $("[phantom] .medal").clone();
      EntryRow.find(".name").text( entry );
      EntryList.append(EntryRow);
    }
  }

  editExp() {
    var c = confirm("Editing the exp will leave a permanent [EDITED] mark, unless resettet to 0, be carefull. Want to continue?");
    if (!c) { return; }

    var new_exp = $(`${this.modal_id} [name=exp]`).val();
    this.update( {exp: new_exp} );
  }

  editCurrency() {
    var new_currency = $(`${this.modal_id} [name=currency]`).val();
    this.update( {currency: new_currency} );
  }

  addMedal() {
    var new_medal = $("#new_medal").val();
    if (isEmpty(new_medal)) { return; }

    var req = {
      "medal_name": new_medal,
      "medal_action": "add"
    };
    var LevelO = this;
    var successfunc = function() {
      $("#new_medal").val("");
      LevelO.current_user_medal.push(new_medal);
      LevelO.buildDetailMedal(LevelO.current_user_medal);
    }
    var failfunc = function () {
      $("#new_medal").val("");
    }
    this.update(req, successfunc, failfunc);
  }

  removeMedal(HTMLButton) {
    var Entry = $(HTMLButton).closest(".medal");
    var medal_name = Entry.find(".name").text();

    var req = {
      "medal_name": medal_name,
      "medal_action": "remove"
    };
    var LevelO = this;
    this.update(req, function () {
      var i = LevelO.current_user_medal.indexOf(medal_name);
      LevelO.current_user_medal.splice(i, 1);
      LevelO.buildDetailMedal(LevelO.current_user_medal);
    });
  }

  setOnServerFalse() {
    var c = confirm("It seems, this member is not on the server anymore and Phaaze did not catch this.\n"+
      "Do you want to set this member to a inactive state?\n"+
      "(This action can not be undone until the member joins the server again)");
    if (!c) { return; }

    var req = {
      "on_server": false
    };
    var LevelO = this;
    var suc = function () {
      $(LevelO.modal_id).modal("hide");
      LevelO.show({offset:LevelO.offset});
    }
    this.update(req, suc);
  }

  update(level_update, success_function, fail_function) {
    var guild_id = $("#guild_id").val();
    level_update["guild_id"] = guild_id;
    var member_id = $(this.modal_id).attr("edit-member");
    level_update["member_id"] = member_id;

    $.post("/api/discord/levels/edit", level_update)
    .done(function (data) {

      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});

      if (success_function) { success_function.call() }

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error updating levels"} );
      if (fail_function) { fail_function.call() }
    })
  }

});
