function showEmail() {
  // i do this, so spam bots don't get the email from the site so easy
  $("#email_icon").popover({
    content: ["admin","@", "pha", "aze", ".", "net"].join(""),
    placement:"bottom",
    trigger:"hover"
  }).popover()
}

function extractData(o) {
  if (typeof o != "object") { o = $(o); }
  let data = {};
  for (f of o.find('[name]')) {
    f = $(f);
    let name = f.attr('name');
    if (f.attr("type") == "checkbox") {
      if (f.is(":checked")) { data[name] = 1; }
      else { d[name] = 0; }
    }
    else {
      let value = f.val();
      data[name] = value;
    }
  }
  return data;
}

function insertData(o, d) {
  if (typeof o != "object") { o = $(o); }
  for (var k in d) {
    try { o.find("[name="+k+"]").val(d[k]); }
    catch (e) { continue }
  }
}

var SessionManager = new (class {
  constructor() {
  }
  showAccountPanel(field="all") {
    $('#login_form').modal('show');
    $('#login_form [table], #login_form [table] [loggedin]').hide();
    $('#login_form [table='+field+']').show();
    if (field != "all") {
      this.getAccountInfo(field);
    }
  }

  getAccountInfo(platform) {
    var SessMan = this;
    $.get("/api/account/"+platform+"/get")
    .done(function (data) {
      SessMan.displayInfo(platform, data.user);
      $('#login_form [table='+platform+'] [loggedin=true]').show();
    })
    .fail(function (data) {
      $('#login_form [table='+platform+'] [loggedin=false]').show();
    })
  }

  displayInfo(platform, data) {
    if (platform == "phaaze") {
      $("#current_phaaze_username").val(data.username);
      $("#current_phaaze_email").val(data.email);
      var role_field = $("#user_roles").html("");
      for (var role of data.roles) {
        role_field.append( $('<div class="role">').text(role) );
      }
    }
    if (platform == "discord") {
      $("#current_discord_username").val(data.username);
      $("#current_discord_avatar").attr(
        "src",
        "https://cdn.discordapp.com/avatars/"+data.user_id+"/"+data.avatar+"?size=256"
      );
    }
  }

  login() {
    let user = $("#phaaze_email_or_username").val();
    let password = $("#phaaze_password").val();
    $.post("/api/account/phaaze/login", {"phaaze_username":user, "phaaze_password":password})
    .done(function (data) {
      CookieManager.set("phaaze_session", data.phaaze_session, data.expire);
      Display.showMessage({'content': 'You successfull logged in!' ,'color':Display.color_success});
      $('#login_form').modal('hide');
    })
    .fail(function (data) {
      $("#phaaze_email_or_username").addClass("animated shake");
      $("#phaaze_password").addClass("animated shake").val("");
      setTimeout(function () {
        $("#phaaze_password, #phaaze_email_or_username").removeClass("animated shake");
      }, 1000);
    })
  }

  logout(field) {
    $.post("/api/account/"+field+"/logout")
    .done(function (data) {
      Display.showMessage({'content': 'You successfull logged out from '+field ,'color':Display.color_success});
      CookieManager.remove(field+"_session");
      $('#login_form').modal('hide');
    })
    .fail(function (data) {
      Display.showMessage({'content': 'Unable to logout', 'color':Display.color_critical});
      console.log(data);
    })
  }

  edit() {
    var data = extractData("#login_form [table=phaaze] [loggedin=true]");
    $.post("/api/account/phaaze/edit", data)
    .done(function (data) {
      Display.showMessage({content:data.msg, color:Display.color_success});
    })
    .fail(function (data) {
      let msg = data.responseJSON ? data.responseJSON.msg : "unknown"
      Display.showMessage({content:msg, color:Display.color_critical});
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
  set(name, value, expire) {
    if (expire == null) {expire = "";}
    else { expire = new Date(expire); }
    document.cookie = name+"="+value+'; expires='+expire+'; Path=/';
  }
  remove(name) {
    document.cookie = name+"=; expires=Thu, 01 Jan 1970 00:00:00 UTC; Path=/"
  }
})()

var Display = new (class {
  constructor() {
    this.color_success = "#38ca35";
    this.color_warning = "#e7b23c";
    this.color_critical = "#e83d3d";
    this.color_info = "#4285FF";
  }
  showMessage(m) {
    if (m == null) { throw "missing message"; }
    if (m.content == null) { throw "missing message content"; }
    if (m.time == null) { m.time = 10000; }
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

// load finished, add events
$("document").ready(function () {

})
