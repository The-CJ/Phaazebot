function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function isEmpty(o) {
  // null
  if (o == null) { return true; }
  // string
  if (typeof o == "string") { if (o != "") { return false; } }
  // number
  if (typeof o == "number") { if (o != 0) { return false; } }
  // object
  for (var v in o) {
    if (o.hasOwnProperty(v)) {
      return false
    }
  }
  return true;
}

function showEmail() {
  // i do this, so spam bots don't get the email from the site so easy
  $("#email_icon").popover({
    content: ["admin","@", "pha", "aze", ".", "net"].join(""),
    placement:"bottom",
    trigger:"hover"
  }).popover()
}

function resetInput(o) {
  // o = JQuery object | str

  // 'o' is the target, in which all [name] elements get looped
  // and filled with a "neutral" state,
  // means empty strings in input fields and unchecked checkboxes

  // checkbox can be overwritten by [checked]
  // input fields can be overwritten by there [value] attribute
  // does not edit <data> elements!
  if (typeof o != "object") { o = $(o); }
  for (var f of o.find('[name]')) {
    f = $(f);

    // ignore data elements
    if ( f.is("data") ) { continue; }

    // is checkbox
    if (f.attr("type") == "checkbox") {
      f.prop( "checked", (f.is("[checked]") ? true : false) );
    }
    // any other type of element
    else {
      var pre_val = f.attr("value");
      f.val( pre_val ? pre_val : "" );
    }
  }
}

function extractData(o) {
  // o = JQuery object | str

  // 'o' is the target, in which all [name] elements get looped
  // and there .val() is stored with there attr('name') as this key
  // multiple same names overwrite each other, last one counts

  // if element is [type=checkbox] then data[name],
  // is 0 or 1 based on checked prop
  if (typeof o != "object") { o = $(o); }
  let data = {};
  for (var f of o.find('[name]')) {
    f = $(f);
    let name = f.attr('name');
    if (f.attr("type") == "checkbox") {
      if (f.is(":checked")) { data[name] = 1; }
      else { data[name] = 0; }
    }
    else {
      let value = f.val();
      data[name] = value;
    }
  }
  return data;
}

function insertData(Obj, data, to_string=false) {
  // obj = JQuery object | str
  // data = object
  // to_string = bool :: false

  // 'obj' is the target, in this target all keys of 'data' get searched
  // every matching [name=key] element, it inserts data[key]

  // if matching element is a [type=checkbox]:
  // element gets prop 'checked' set based on boolish interpretion of data[key]

  // if matching element is a SPAN
  // the value of data[key] gets inserted as text

  // to_string ensures content input by all types, except 'null'
  // which will be convertet to a empty string

  if (typeof Obj != "object") { Obj = $(Obj); }
  for (var key in data) {
    try {
      var value = data[key];

      // ensure stings?
      if (to_string) {
        if (typeof value == "boolean") { value = (value ? "true" : "false"); }
        else if (value == null) { value = ""; }
      }

      // find all elements based on [name]
      for (var Match of Obj.find(`[name=${key}]`)) {
        Match = $(Match);

        // checkboxes
        if (Match.attr("type") == "checkbox") {
          let checked = ( value ? true : false );
          Match.prop("checked", checked);
          continue;
        }

        if ( ["SPAN"].indexOf(Match.prop("tagName")) >= 0 ) {
          Match.text(value);
          continue;
        }

        Match.val(value);
        continue;
      }
    }
    catch (e) { continue }
  }
}

function oppositeValue(v) {
  if (typeof v == "object") { throw "can't switch object type"; }
  else if (typeof v == "boolean") { return !v }
  else if (typeof v == "number") { return v * -1 }
  else if (typeof v == "string") {
    // if string, interpret values for a bool type
    // the strings "0", "false" and "" are often used to represent a false statement, so return true
    if (v == "0" || v == "false" || !v) { return true; }
    // everything else is true in string language
    else { return false; }
  }
  else {
    throw "unknown object handler";
  }

}

function generalAPIErrorHandler(x={}) {
  // it does what you whould think it does,
  // give this function the data object from a $.get .post .etc...
  // and it will give you a display message,
  // with the message, or at least the error... mostly
  // also sends stuff to debug log

  // message content priority
  // server message -> alternativ message -> server error code -> "Unknown"

  // x : data :: jquery response
  // x : msg :: str
  // x : color :: str
  // x : time :: int
  // x : no_message :: bool

  var data = x["data"] ? x["data"] : null;
  var color = x["color"] ? x["color"] : Display.color_critical;
  var time = x["time"] ? x["time"] : this.default_time;
  var alt_msg = x["msg"] ? x["msg"] : null;

  // most likely alwys is true, since this is a ERROR function
  if (data.responseJSON) { data = data.responseJSON; }

  var final_message = null;

  // server gave us a 'msg'
  if (data.msg) { final_message = data.msg; }
  // server has not 'msg' but user gave one
  else if (alt_msg) { final_message = alt_msg; }
  // no 'msg' at all take server 'error'
  else if (alt_msg) { final_message = data.error; }
  // no 'msg' or 'error'... means "unknown"
  else { final_message = "Unknown error"; }

  if (!x["no_message"]) {
    Display.showMessage( {content:final_message, color:color, time:time} );
  }
  console.log(data);
}

var SessionManager = new (class {
  constructor() {
  }

  showAccountPanel(field="all") {
    $('#account_modal').modal('show');
    $('#account_modal [table], #account_modal [login]').hide();
    $(`#account_modal [table=${field}]`).show();
    if (field != "all") {
      this.getAccountInfo(field);
    }
  }

  getAccountInfo(platform) {
    var SessMan = this;
    $.get(`/api/account/${platform}/get`)
    .done(function (data) {
      SessMan.displayInfo(platform, data.user);
      $(`#account_modal [table=${platform}] [login=true]`).show();
    })
    .fail(function (data) {
      $(`#account_modal [table=${platform}] [login=false]`).show();
    })
  }

  displayInfo(platform, data) {
    if (platform == "phaaze") {
      insertData("#account_modal [table=phaaze] [login=true]", data);
      var RoleList = $("#account_modal_roles").html("");
      for (var role of data.roles) {
        RoleList.append( $("<div class='role'>").text(role) );
      }
    }
    if (platform == "discord") {
      $("#current_discord_username").val(data.username);
      $("#current_discord_avatar").attr(
        "src",
        `https://cdn.discordapp.com/avatars/${data.user_id}/${data.avatar}?size=256`
      );
    }
  }

  login() {
    var login = extractData("#account_modal [table=phaaze] [login=false]");
    $.post("/api/account/phaaze/login", login)
    .done(function (data) {
      CookieManager.set("phaaze_session", data.phaaze_session, data.expires_in);
      Display.showMessage({'content': 'You successfull logged in!' ,'color':Display.color_success});
      $('#account_modal').modal('hide');
    })
    .fail(function (data) {
      // pun = phaaze user name
      // ppw = phaaze pass word
      $("#pun").addClass("animated shake");
      $("#ppw").addClass("animated shake").val("");
      setTimeout(function () {
        $("#pun, #ppw").removeClass("animated shake");
      }, 1000);
    })
  }

  logout(platform) {
    $.post(`/api/account/${platform}/logout`)
    .done(function (data) {
      Display.showMessage({"content": `You successfull logged out from ${platform}`,'color':Display.color_success});
      if (platform == "phaaze") { CookieManager.remove("phaaze_session"); }
      if (platform == "discord") { CookieManager.remove("phaaze_discord_session"); }
      if (platform == "twitch") { CookieManager.remove("phaaze_twitch_session"); }
      $('#account_modal').modal('hide');
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"Unable to logout"} );
    })
  }

  edit() {
    var data = extractData("#account_modal [table=phaaze] [login=true]");
    $.post("/api/account/phaaze/edit", data)
    .done(function (data) {
      Display.showMessage({content:data.msg, color:Display.color_success});
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"Editing failed."} );
    })
  }
})()

var CookieManager = new (class {
  constructor() {

  }
  get(cookie) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
  }
  set(name, value, expires_in) {
    if (expires_in == null) {
      document.cookie = name+'='+value+'; Path=/';
    }
    else {
      document.cookie = name+'='+value+'; Max-Age=' + expires_in + '; Path=/';
    }
  }
  remove(name) {
    document.cookie = name+"=; Max-Age=-1; Path=/"
  }
})()

var Display = new (class {
  constructor() {
    this.color_success = "#38ca35";
    this.color_warning = "#e7b23c";
    this.color_critical = "#e83d3d";
    this.color_info = "#4285FF";
    this.default_time = 10000;
  }
  showMessage(m) {
    if (m == null) { throw "missing message"; }
    if (m.content == null) { throw "missing message content"; }
    if (m.time == null) { m.time = this.default_time; }
    if (m.color == null) { m.color = this.color_info; }
    if (m.text_color == null) { m.text_color = "#fff"; }

    // the main display field is located in the navbar, so its everywere.
    var messagebox = $('[messagebox]');

    var mid = (Math.floor(Math.random()*1000000));
    var message = $('<div class="message" onclick="$(this).remove()"><h1></h1></div>');
    message.attr("mid", mid);
    message.css("animation-duration", m.time+"ms");
    var messagebar_raw = $('<div class="messagebar_raw"></div>');
    var messagebar_time_left = $('<div class="messagebar_time_left"></div>');
    messagebar_time_left.css("animation-duration", m.time+"ms");

    // build message
    message.find("h1").text(m.content);
    messagebar_raw.append(messagebar_time_left);
    message.append(messagebar_raw);

    // add style
    message.css('background', m.color);
    message.css('color', m.text_color);

    // append and start remove timer
    messagebox.append(message);

    setTimeout(
      function () { $('[messagebox] > [mid='+mid+']').remove(); },
      m.time
    );
  }
})()

var DynamicURL = new (class {
  constructor() {
    this.values = {};
  }

  set(key, value, update=true) {
    this.values[key] = value;
    if (update) { this.update(); }
  }

  get(key) {
    let value = this.values[key];
    if (value == null) {
      value = this.getFromLocation(key);
    }
    return value
  }

  update() {
    let ucurl = window.location.pathname;
    let pre = "?";

    for (var key in this.values) {
      let value = this.values[key];
      if (isEmpty(value)) { continue; }

      ucurl = ucurl + pre + key + "=" + value;
      pre = "&";

    }
    window.history.replaceState('obj', 'newtitle', ucurl);
  }

  getFromLocation(name) {
    let url = window.location.href;
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
  }

})

// load finished, add events
$("document").ready(function () {

})
