function logo_rotate() {
  let ml = $('#main_logo');
    ml.one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function () {
    ml.removeClass('rotateIn');
    ml.addClass('animation-spin');
  });
  ml.dblclick(function () {
    window.location = "/admin";
    return false;
  });
}

$('document').ready(logo_rotate);
