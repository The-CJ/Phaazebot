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

  login() {

  }
  logout() {

  }
})()

// load finished, add events
