function phaaze_logout() {
  var x = getCookie("phaaze_session");
  var r = {};
  r['phaaze_session'] = x;
  $.post("/api/account/logout", JSON.stringify(r), function (data) {
    remCookie("phaaze_session");
    location.reload();
  })
}

function phaaze_login() {
  var login = $("#phaaze_loginname").val();
  var password = $("#phaaze_password").val();

  var r = {};

  r["username"] = login;
  r["password"] = password;

  $.post("/api/account/login", r)
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

//

function extract_data(query_obj) {
  let d = {};
  for (field of query_obj.find('[name]')) {
    field = $(field);
    let name = field.attr('name');
    let value = field.val();

    d[name] = value;
  }
  return d;
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

function _show_message(content, color, text_color, symbol, link, time) {
  // The display field is located in the main navbar, so its everywere.
  var message_field = $('#_message_field');

  var message = $('<div class="_message"><h1></h1></div>');
  var message_bar_raw = $('<div class="_message_bar_raw"></div>')
  var message_bar_time = $('<div class="_message_bar_left"></div>')

  message.find('h1').text(content);
  message_bar_raw.append(message_bar_time)
  message.append(message_bar_raw);

  if (time != null) {
    message_bar_time.css('animation-duration', time+'ms');
    message.css('animation-duration', time+'ms');
  } else {
    time = 10000;
  }

  if (color != null) {
    message.css('background', color);
  } else {
    message.css('background', '#4285FF');
  }

  if (text_color != null) {
    message.css('color', text_color);
  } else {
    message.css('color', 'white');
  }

  message_field.append(message);

  setTimeout(function () {
    message.remove();
  }, time);

}

$('document').ready(function () {
  Waves.attach('.btn', ['waves-effect', 'waves-light']);
  Waves.attach('.nav-link', ['waves-effect', 'waves-light']);
});
