function discord_logout() {
  var x = getCookie("discord_session");
  var asd = $("#asd").val();
  var r = {};
  r['discord_session'] = x;
  $.post("/api/discord/logout", JSON.stringify(r), function (data) {
    document.cookie = "discord_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC;"
    window.location = "/discord";
  })
}


function getCookie(cname) {
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