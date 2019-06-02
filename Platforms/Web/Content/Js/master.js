function showEmail() {
  // i do this, so spam bots don't get the email from the site so easy
  $("#email_icon").popover({
    content: ["admin","@", "pha", "aze", ".", "net"].join(""),
    placement:"bottom",
    trigger:"hover"
  }).popover()
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
    $.get("/api/account/"+platform+"/get")
    .done(function (data) {
      $('#login_form [table='+platform+'] [loggedin=true]').show();
      console.log(data);
    })
    .fail(function (data) {
      $('#login_form [table='+platform+'] [loggedin=false]').show();
    })
  }

  login() {
    let user = $("#phaaze_email_or_username").val();
    let password = $("#phaaze_password").val();
    $.post("/api/account/phaaze/login", {"phaaze_username":user, "phaaze_password":password})
    .done(function (data) {
      CookieManager.set("phaaze_session", data.phaaze_session);
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

// load finished, add events
$("document").ready(function () {

})
