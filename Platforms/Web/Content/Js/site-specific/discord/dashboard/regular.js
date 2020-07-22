var Regulars = new(class {
  constructor() {
    this.modal_id = "#regular_modal";
    this.list_id = "#regular_list";
    this.total_field_id = "#regular_amount";
    this.phantom_class = ".regular";

    this.default_limit = 50;
    this.default_page = 0;

    this.current_limit = 0;
    this.current_page = 0;
    this.current_max_page = 0;
  }

  show() {
    // loads in default values or taken from url
    let limit = DynamicURL.get("regulars[limit]") || this.default_limit;
    let page = DynamicURL.get("regulars[page]") || this.default_page;

    var req = {
      limit: limit,
      offset: (page * limit)
    };

    this.load( req );
  }

  load(x={}) {
    var RegularO = this;
    x["guild_id"] = $("#guild_id").val();
    x["detailed"] = true;

    $.get("/api/discord/regulars/get", x)
    .done(function (data) {

      // update view
      RegularO.updatePageIndexButtons(data);

      var EntryList = $(RegularO.list_id).html("");
      $(RegularO.total_field_id).text(data.total);

      for (var entry of data.result) {
        var Template = $(`[phantom] ${RegularO.phantom_class}`).clone();

        // set avatar
        var avatar = discordUserAvatar(entry.member_id, entry.avatar);
        Template.find("img").attr("src", avatar);

        insertData(Template, entry);
        Template.attr("regular-id", entry.regular_id);

        EntryList.append(Template);
      }

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load regulars"} );
    })
  }

  // utils
  nextPage(last=false) {
    this.current_page += 1;
    if (last) { this.current_page = this.current_max_page; }

    var search = extractData("[location=regulars] .controls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  prevPage(first=false) {
    this.current_page -= 1;
    if (first) { this.current_page = 0; }

    var search = extractData("[location=regulars] .controls");
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
      DynamicURL.set("regulars[limit]", this.current_limit);
    } else {
      DynamicURL.set("regulars[limit]", null);
    }

    // update page url if needed
    if (this.current_page != this.default_page) {
      DynamicURL.set("regulars[page]", this.current_page);
    } else {
      DynamicURL.set("regulars[page]", null);
    }

    // update html elements
    $("[location=regulars] [name=limit]").val(this.current_limit);
    $("[location=regulars] .pages .prev").attr("disabled", (this.current_page <= 0) );
    $("[location=regulars] .pages .next").attr("disabled", (this.current_page >= this.current_max_page) );
    $("[location=regulars] .pages .page").text(this.current_page+1);
  }

  showStep(step=1) {
    $(`${this.modal_id} [step]`).hide();
    $(`${this.modal_id} [step=${step}]`).show();
  }

  search() {
    var RegularO = this;
    var data = extractData(`${this.modal_id} [step=1]`);
    var search_user = data.search_user || "";

    var x = {};
    x["search"] = "member";
    x["term"] = search_user;
    x["guild_id"] = $("#guild_id").val();

    $.get("/api/discord/search", x)
    .done(function (data) {

      RegularO.showStep(2);
      let avatar = discordUserAvatar(data.result.id, data.result.avatar, 128);
      $(`${RegularO.modal_id} [step=2] img`).attr("src", avatar);
      data.result.name = `${data.result.name}#${data.result.discriminator}`;
      insertData(`${RegularO.modal_id} [step=2]`, data.result);

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not find a member", time:1250} );
    });
  }

  //  create
  createModal() {
    resetInput(this.modal_id);
    this.showStep(1);
    $(this.modal_id).attr("mode", "create");
    $(this.modal_id).modal("show");
  }

  create() {
    var RegularO = this;
    var x = extractData(`${this.modal_id} [step=2]`);
    x["member_id"] = x.id;
    x["guild_id"] = $("#guild_id").val();

    $.post("/api/discord/regulars/create", x)
    .done(function (data) {

      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      $(RegularO.modal_id).modal("hide");
      RegularO.show();

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not add new regular"} );
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

  // delete

});
