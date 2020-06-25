$("document").ready(function () {
  PublicLevels.show();
})

var PublicLevels = new(class {
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
  }

  show() {
    // loads in default values or taken from url
    let limit = DynamicURL.get("limit") || this.default_limit;
    let page = DynamicURL.get("page") || this.default_page;

    var req = {
      limit: limit,
      offset: (page * limit)
    };

    this.load( req );
  }

  load(x={}) {
    var PublicLevelsO = this;
    x["guild_id"] = $("#guild_id").val();
    x["detailed"] = true;

    $.get("/api/discord/levels/get", x)
    .done(function (data) {

      // update view
      PublicLevelsO.updatePageIndexButtons(data);

      var LevelList = $(PublicLevelsO.list_id).html("");
      $(PublicLevelsO.total_field_id).text(data.total);

      for (var level of data.result) {
        var Template = $(`[phantom] ${PublicLevelsO.phantom_class}`).clone();

        // set avatar
        var avatar = discordUserAvatar(level.member_id, level.avatar);
        Template.find("img").attr("src", avatar);

        insertData(Template, level);
        Template.attr("member-id", level.member_id);

        if (level.edited) {
          Template.find(".level-exp").addClass("red");
          Template.find(".level-exp").attr("title", "This member got edited, the stats can be wrong");
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
    var search = extractData(".controlls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  prevPage(first=false) {
    this.current_page -= 1;
    if (first) { this.current_page = 0; }

    var search = extractData(".controlls");
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
    $(".controlls [name=limit]").val(this.current_limit);
    $(".controlls .pages .prev").attr("disabled", (this.current_page <= 0) );
    $(".controlls .pages .next").attr("disabled", (this.current_page >= this.current_max_page) );
    $(".controlls .pages .page").text(this.current_page+1);
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
      let curr_single = $("#guild_currency").val();
      let curr_multi = $("#guild_currency_multi").val();
      level.currency_text = level.currency + ' ' + (this.currency == 1 ? curr_single : curr_multi);
      level.exp_text = `${level.exp}`;
      level.level_text = `${level.level}`;
      level.display_rank = (level.rank ? `Rank: #${level.rank}` : "Rank: [N/A]");
      level.display_id = (level.member_id ? `ID: ${level.member_id}` : "ID: [N/A]");

      // set avatar
      var avatar = discordUserAvatar(level.member_id, level.avatar, 128);
      $(`${LevelO.modal_id} img`).attr("src", avatar);

      insertData(LevelO.modal_id, level);
      LevelO.loadinModalMedal(level.guild_id, level.member_id);
      $(LevelO.modal_id).modal("show");

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"Could not load level details"} );
    });
  }

});
