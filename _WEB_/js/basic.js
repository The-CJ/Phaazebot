function phaaze_logout() {
  var x = getCookie("phaaze_session");
  var r = {};
  r['phaaze_session'] = x;
  $.post("/api/logout", JSON.stringify(r), function (data) {
    remCookie("phaaze_session");
    location.reload();
  })
}

function phaaze_login() {
  var login = $("#phaaze_loginname").val();
  var password = $("#phaaze_password").val();

  var r = {};

  r["phaaze_username"] = login;
  r["password"] = password;

  $.post("/api/login", JSON.stringify(r))
  .done(
    function (data) {
      $('#phaaze_loginname').addClass("animated bounceOutLeft");
      $('#phaaze_password').addClass("animated bounceOutRight");
      $('#sub_button').addClass("animated flipOutX");
      setTimeout(function () {
        setCookie("phaaze_session", data.phaaze_session);
        location.reload();
      },1000);
    }
  )
  .fail(
    function (data) {
      if (data.responseJSON.error == 'missing_data') {
        $('#phaaze_loginname').addClass("animated pulse");
        $('#phaaze_password').addClass("animated pulse");
        setTimeout(function () {
          $('#phaaze_loginname').removeClass("animated pulse");
          $('#phaaze_password').removeClass("animated pulse");
        },1000);
        return ;
      }
      if (data.responseJSON.error == "wrong_data") {
        $('#phaaze_loginname').addClass("animated shake");
        $('#phaaze_password').addClass("animated shake");
        $('#sys_msg').text("Password or Login Name wrong.");
        $('#phaaze_password').val("");
        setTimeout(function () {
          $('#phaaze_loginname').removeClass("animated shake");
          $('#phaaze_password').removeClass("animated shake");
        },1000);
        return ;
      }
    }
  );
}

var entityMap = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
  '/': '&#x2F;',
  '`': '&#x60;',
  '=': '&#x3D;'
};

function escapeHtml (string) {
  return String(string).replace(/[&<>"'`=\/]/g, function (s) {
    return entityMap[s];
  });
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

function setCookie(name, value) {
  document.cookie = name+"="+value+'; Path=/';
}

function remCookie(name) {
  document.cookie = name+"=; expires=Thu, 01 Jan 1970 00:00:00 UTC; Path=\"/\""
}

function copy_clipboad(field) {
  var copyText = document.getElementById(field);
  copyText.select();
  document.execCommand("Copy");
}

function copy_data_fields(from, to) {
  var from_val = $('#'+from).val();
  $('#'+to).val(from_val);
}

function _show_message(content, style) {
  // The display field is located in the main navbar, so its everywere.
  var message_field = $('#_message_field');

  var id_ = "msg_field_" + Math.floor((Math.random() * 10000) + 1);
  var outer_field = $('<div class="message_box"></div>');
  var inner_field = $('<div style="margin:1em;"></div>');
  inner_field.text(content);

  outer_field.attr('style', style);
  outer_field.attr('id', id_);
  outer_field.html(inner_field);

  message_field.append(outer_field);

  setTimeout(function () {
    $('#'+id_).remove();
  }, 5000);

}