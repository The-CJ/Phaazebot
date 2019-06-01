function showEmail() {
  // i do this, so spam bots don't get the email from the site so easy
  $("#email_icon").popover({
    content: ["admin","@", "pha", "aze", ".", "net"].join(""),
    placement:"bottom",
    trigger:"hover"
  }).popover()
}

SessionManager = new (class SessionManager {
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

  }
  logout() {

  }
})()

// load finished, add events
$("document").ready(function () {

})
