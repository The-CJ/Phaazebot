$("document").ready(async function () {
  DiscordDashboard.loadGeneralInfo();
  await sleep(250);
  DiscordDashboard.restoreView();
})

var DiscordDashboard = new (class {
  constructor() {
    this.channels = [];
    this.roles = [];
  }

  loadLocation(target) {
    // handles all display and view utils
    // everything except home is suppost to be outmoved in a extra class
    DynamicURL.set("view", target);

    if (target == "home") {
      this.setSitePanelSelectedLocation("home");
      var guild_id = $("#guild_id").val();
      $.get("/api/discord/guild", {guild_id: guild_id})
      .done(function (data) {
        var guild = data.result;

        var image = discordGuildAvatar(guild.id, guild.icon, 128);
        $("#icon").attr("src", image);

        insertData("[location='home']", guild);
      })
      .fail(function (data) {
        generalAPIErrorHandler( {data:data, msg:"loading informations failed"} );
      });
    }

    if (target == "quotes") {
      this.setSitePanelSelectedLocation("quotes");
      Quotes.show();
    }

    if (target == "twitch_alerts") {
      this.setSitePanelSelectedLocation("twitch_alerts");
      TwitchAlerts.show();
    }

    if (target == "levels") {
      this.setSitePanelSelectedLocation("levels");
      Levels.show();
    }

    if (target == "configs_chat") {
      this.setSitePanelSelectedLocation("configs");
      ConfigsChat.show();
    }

    this.setLocationWindow(target);
    this.setSitePanelCollapse("hide");
  }

  __loadConfig() {
    DynamicURL.set("view", "configs");
    this.showLocationWindow("configs");
    Configs.show();
  }

  __loadCommand() {
    DynamicURL.set("view", "commands");
    this.showLocationWindow("commands");
    Commands.show();
  }

  __loadLevel() {
    DynamicURL.set("view", "levels");
    this.showLocationWindow("levels");
    Levels.show();
  }

  __loadAssignRole() {
    DynamicURL.set("view", "assign_roles");
    this.showLocationWindow("assign_roles");
    AssignRoles.show();
  }

  // utils
  loadGeneralInfo() {
    var DashO = this;
    var guild_id = $("#guild_id").val();
    // same api call as in loadHome, but why not
    $.get("/api/discord/guild", {guild_id: guild_id})
    .done(function (data) {

      DashO.channels = data.result.channels;
      DashO.roles = data.result.roles;

      DashO.buildDiscordChannelSelect({"channel_list":DashO.channels});
      DashO.buildDiscordRolesSelect({"role_list":DashO.roles})

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"Error loading general informations"} );
    })
  }

  buildDiscordChannelSelect(x) {
    // fill a select HTML Object with discord channels.
    // the setting can be taken from the html element or from the function call
    // function call is dominant

    // used field in object x
    // x["channel_list"] :: a list of `channel objects` {"id":"123456", "name":"something", "channel_type":"text"}
    // x["target"] :: a list of jquery select elements, or a string for a jquery search   [Default: "select[discord-channel]"]
    // x["include_none"] :: bool, if true, include a <option value=''>(None)</option> at first [Default: false]
    //   also true if Select HTML element has attribute: discord-channel-none=true
    // x["only_type"] :: string, if not emtpy, only list the matching types [Default: ""]
    //   also set by using the attribute: [discord-channel=text] or [discord-channel=voice]

    var HTMLSelectList = null;

    var channel_list = x["channel_list"]; if (isEmpty(channel_list)) {throw "empty channel_list";}
    var include_none = x["include_none"];
    var only_type = x["only_type"];
    var target = x["target"];
    if (target == undefined) { HTMLSelectList = $("select[discord-channel]"); }
    else if (typeof target == "string") { HTMLSelectList = $(target); }
    if (isEmpty(HTMLSelectList)) { throw "no targets"; }

    for (var HTMLSelect of HTMLSelectList) {
      // clear first
      HTMLSelect = $(HTMLSelect).html("");

      // per element vars
      var element_only_type = only_type == undefined ? HTMLSelect.attr("discord-channel") : only_type;
      var element_include_none = include_none == undefined ? HTMLSelect.attr("discord-channel-none") : include_none;

      // include a none?
      if ( element_include_none ) { HTMLSelect.append("<option value=''>(None)</option>"); }

      for (var channel of channel_list) {
        // make copy of name, since we keep the channellist untouched
        var name = channel.name;
        var id = channel.id;

        // only type?
        if (element_only_type) {
          if (element_only_type != channel.channel_type) { continue; }
        }

        // special format
        if (channel.channel_type == "text") { name = "#" + name;  }

        var Option = $("<option>");
        Option.text(name);
        Option.attr("value", id);
        HTMLSelect.append(Option);
      }
    }
  }

  buildDiscordRolesSelect(x) {
    // fill a select HTML Object with discord roles.
    // the setting can be taken from the html element or from the function call
    // function call is dominant

    // used field in object x
    // x["role_list"] :: a list of `role objects` {"id":"123456", "name":"something", "managed":false}
    // x["target"] :: a list of jquery select elements, or a string for a jquery search   [Default: "select[discord-role]"]
    // x["include_none"] :: bool, if true, include a <option value=''>(None)</option> at first [Default: false]
    //   also true if Select HTML element has attribute: [discord-role-none=true]
    // x["show_managed"] :: bool, if true, include managed roles in the select [Default: false]
    //   also true if Select HTML element has attribute: [discord-role-managed=true]

    var HTMLSelectList = null;

    var role_list = x["role_list"]; if (isEmpty(role_list)) {throw "empty role_list";}
    var include_none = x["include_none"];
    var show_managed = x["show_managed"];
    var target = x["target"];
    if (target == undefined) { HTMLSelectList = $("select[discord-role]"); }
    else if (typeof target == "string") { HTMLSelectList = $(target); }
    if (isEmpty(HTMLSelectList)) { throw "no targets"; }

    for (var HTMLSelect of HTMLSelectList) {
      // clear first
      HTMLSelect = $(HTMLSelect).html("");

      // per element vars
      var element_show_managed = show_managed == undefined ? HTMLSelect.attr("discord-role-managed") : show_managed;
      var element_include_none = include_none == undefined ? HTMLSelect.attr("discord-role-none") : include_none;

      // include a none?
      if ( element_include_none ) { HTMLSelect.append("<option value=''>(None)</option>"); }

      for (var role of role_list) {
        // make copy of name, since we keep the rolelist untouched
        var name = role.name;
        var id = role.id;

        // managed role?
        if (!element_show_managed && role.managed) { continue; }

        var Option = $("<option>");
        Option.text(name);
        Option.attr("value", id);
        HTMLSelect.append(Option);
      }
    }
  }

  // getter
  getDiscordChannelByID(id) {
    for (var channel of this.channels) {
      if (channel.id == id) { return channel; }
    }
    return null;
  }

  getDiscordRoleByID(id) {
    for (var role of this.roles) {
      if (role.id == id) { return role; }
    }
    return null;
  }

  // view utils
  setLocationWindow(view) {
    // set the selected parts in main-panel
    // also updates DynamicURL
    // empty to hide everything
    if ( isEmpty(view) ) { view = null; }
    DynamicURL.set("view", view);
    $("[location]").hide();
    $(`[location=${view}]`).show();
  }

  setSitePanelCollapse(state) {
    // controlls site panel and collapse button visibility, classes, etc
    // allowed states: "show", "hide", ""
    // empty will toggle it
    if ( isEmpty(state) ) {
      state = $(".site-panel").hasClass("show");
      state = state ? "hide" : "show";
    }

    if (state == "hide") { $(".site-panel, .site-panel-btn").removeClass("show"); }
    else if (state == "show") { $(".site-panel, .site-panel-btn").addClass("show"); }
  }

  setSitePanelSelectedLocation(target) {
    // set the background color of the last selected site-panel option
    if ( isEmpty(target) ) { target = null; }
    $(".site-panel [sidebar-location]").removeClass("active");
    $(`.site-panel [sidebar-location="${target}"]`).addClass("active");
  }

  setExpandSitePanelCollapse(expand) {
    // there are multiple collapse elements in the sitebar
    // given a expand name will open this collapse and set it in DynamicURL
    // empty will clear it
    if ( isEmpty(expand) ) { expand = null; }
    DynamicURL.set("ex", expand);
    $(".site-panel .collapse").collapse("hide");
    $(`.site-panel .collapse[expand="${expand}"]`).collapse("show");
  }

  restoreView() {
    // restores all locations and sitebar selections
    // based on DynamicURL
    var expand = DynamicURL.get("ex");
    var location = DynamicURL.get("view");

    if ( isEmpty(expand) ) { expand = null; }
    this.setExpandSitePanelCollapse(expand);

    if ( isEmpty(location) ) { location = "home"; }
    this.loadLocation(location);
  }
})

// utils
function showTokenHelp(field) {
  if (isEmpty(field)) { field = ""; }
  else { field = "."+field; }
  $("#token_modal_help .token").hide();
  $("#token_modal_help .token"+field).show();
  $("#token_modal_help").modal("show");
}
