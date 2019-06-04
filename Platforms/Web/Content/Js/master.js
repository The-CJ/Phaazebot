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

var SessionManager = new (class SessionManager {
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
    $("#current_"+platform+"_username").val(data.username);
    $("#current_"+platform+"_email").val(data.email);
    if (platform == "phaaze") {
      var role_field = $("#user_roles").html("");
      for (var role of data.roles) {
        role_field.append( $('<div class="role">').text(role) );
      }
    }
  }

  login() {
    let user = $("#phaaze_email_or_username").val();
    let password = $("#phaaze_password").val();
    $.post("/api/account/phaaze/login", {"phaaze_username":user, "phaaze_password":password})
    .done(function (data) {
      CookieManager.set("phaaze_session", data.phaaze_session);
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
      console.log(data);
      CookieManager.remove("phaaze_session");
    })
    .fail(function (data) {
      console.log(data);
    })
  }
  edit() {
    var data = extractData("#login_form [table=phaaze] [loggedin=true]");
    $.post("/api/account/phaaze/edit", data)
    .done(function (data) {
      console.log(data);
    })
    .fail(function (data) {
      console.log(data);
    })
  }
})()

var CookieManager = new (class CookieManager {
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
  set(name, value) {
    document.cookie = name+"="+value+'; Path=/';
  }
  remove(name) {
    document.cookie = name+"=; expires=Thu, 01 Jan 1970 00:00:00 UTC; Path=\"/\""
  }
})()

var Display = new (class Display {
  constructor() {

  }
  showMessage(m) {
    if (m == null) { throw "missing message"; }
    if (m.content == null) { throw "missing message content"; }
    if (m.time == null) { m.time = 10000; }
    if (m.color == null) { m.color = "#4285FF"; }
    if (m.text_color == null) { m.text_color = "#fff"; }

    // the main display field is located in the navbar, so its everywere.
    var messagebox = $('[messagebox]');

    var mid = (Math.floor(Math.random()*1000000));
    var message = $('<div class="message" onclick="$(this).remove()"><h1></h1></div>');
    var messagebar_raw = $('<div class="messagebar_raw"></div>');
    var messagebar_time_left = $('<div class="messagebar_time_left"></div>');

    // build message
    message.find("h1").text(m.content);
    messagebar_raw.append(messagebar_time_left);
    message.append(messagebar_raw);
    message.attr("mid", mid);

    // add style
    message.css('background', m.color);
    message.css('color', m.text_color);

    // append and start remove timer
    messagebox.append(message);

    setTimeout(function () {
      $('[messagebox] > [mid='+mid+']').remove();
    }, m.time);
  }
})()

// load finished, add events
$("document").ready(function () {

})
