// Log- in/out

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

// Field data managment

function extract_data(query_obj) {
  let d = {};
  for (field of query_obj.find('[name]')) {
    field = $(field);
    let name = field.attr('name');

    if (field.attr("type") == "checkbox") {
      if (field.is(":checked")) {
        d[name] = 1;
      }
      else {
        d[name] = 0;
      }
    }
    else {
      let value = field.val();
      d[name] = value;
    }

  }
  return d;
}

function insert_data(query_obj, data) {
  if (query_obj == null) {
    throw "insert_data() got 'null' query_obj"
  }
  if (data == null) {
    throw "insert_data() got 'null' data for format"
  }

  for (var key in data) {
    try {
      query_obj.find("[name="+key+"]").val(data[key]);
    } catch (e) {
      continue
    }
  }
}

// Cookie managment

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

// data transfer

function copy_clipboad(field) {
  var copyText = document.getElementById(field);
  copyText.select();
  document.execCommand("Copy");
}

function copy_data_fields(from, to) {
  var from_val = $('#'+from).val();
  $('#'+to).val(from_val);
}

// utils

function upload_file(args, url, success_function, fail_function) {
  if (!(url && args)) {return false;}

  var formData = new FormData();
  for (var upl in args) {
    formData.append(upl, args[upl]);
  }
  var request = new XMLHttpRequest();
  request.onload = function () {
    if (200 <= request.status && request.status < 300) {
      success_function( JSON.parse(request.responseText) );
    } else {
      fail_function( JSON.parse(request.responseText) );
    }
  }
  request.onerror = function () {
    fail_function(JSON.parse(request.responseText));
  }
  request.open("POST", url);
  request.send(formData);
}

// utils - screen

function _show_message(content, color, text_color, symbol, link, time) {
  if (typeof content == "object") {
    color = content["color"];
    text_color = content["text_color"];
    symbol = content["symbol"];
    link = content["link"];
    time = content["time"];
    content = content["content"];
  }

  // The display field is located in the main navbar, so its everywere.
  var message_field = $('#_message_field');

  var message = $('<div class="_message" onclick="$(this).remove()"><h1></h1></div>');
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

function _show_loading(content) {
  if (!content) {content = "Loading..."}
  var load_spot = $('#_loading');
  if (load_spot.is(":empty")) {
    var load_screen = $("<div class=\"loading_screen center-item-row\"</div>");
    var inner_container = $("<div class=\"middle center-item-col\"></div>");
    var image = $("<img class=\"animation-spin\"src=\"/favicon.ico\" alt=\"loading\" onclick=\"_hide_loading()\">");
    var text = $("<span>"+content+"</span>");
    inner_container.append(image);
    inner_container.append(text);
    load_screen.append(inner_container);

    load_spot.append(load_screen);
  }
}

function _hide_loading() {
  $('#_loading').html("");
}

// stuff

$('document').ready(function () {
  Waves.attach('.btn', ['waves-effect', 'waves-light']);
  Waves.attach('.nav-link', ['waves-effect', 'waves-light']);
});
