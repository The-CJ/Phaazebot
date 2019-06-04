function copy_clipboad(field) {
  var copyText = document.getElementById(field);
  copyText.select();
  document.execCommand("Copy");
}

function copy_data_fields(from, to) {
  var from_val = $('#'+from).val();
  $('#'+to).val(from_val);
}

function upload_file(args, url, success_function, fail_function) {
  if (!(url && args)) {return false;}

  var formData = new FormData();
  for (var upl in args) {
    formData.append(upl, args[upl]);
  }
  var request = new XMLHttpRequest();
  request.onload = function () {
    if (200 <= request.status && request.status < 300) {
      success_function( JSONparse(request.responseText) );
    } else if (request.status >= 500) {
      fail_function( Array() );
    } else {
      fail_function( JSONparse(request.responseText) );
    }
  }
  request.onerror = function () {
    fail_function(JSONparse(request.responseText));
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

function edit_wiki_page() {
  var path = window.location.pathname;
  if (!path.startsWith("/wiki")) {return}
  var p = path.slice(6);
  if (p == "") {_show_message("Not a editable page");return}
  window.location = "/wiki?edit="+p;
}

$('document').ready(function () {
  Waves.attach('.btn', ['waves-effect', 'waves-light']);
  Waves.attach('.nav-link', ['waves-effect', 'waves-light']);
});
