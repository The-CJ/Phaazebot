function logoRotate() {
  var ml = $('#mainsite_logo');
  ml.one('animationend', function () {
    ml.removeClass('rotateIn');
    ml.addClass('animation-spin anti-clockwise');
  });
  ml.dblclick(function () {
    window.location = "/admin";
    return false;
  });
}

$('document').ready(function () {
  logoRotate();
});
