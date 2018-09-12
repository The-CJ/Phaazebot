function logo_rotate() {
  var ml = $('#main_logo');
  ml.one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function () {
    ml.removeClass('rotateIn');
    ml.addClass('animation-spin');
  });
  ml.dblclick(function () {
    window.location = "/admin";
    return false;
  });
}

$('document').ready(function () {
  logo_rotate();
});
