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
  document.cookie = name+"="+value+"; Path=\"/\"";
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