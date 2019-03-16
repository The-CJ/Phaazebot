$("document").ready(function () {
  load_images();
})

function load_images() {
  let search = $("[name=image_search]").val();
  var site_index = parseInt($("[name=site_index]").val());
  $.get("/api/admin/manage-image/get", {image:search, limit: 30, offset:site_index*30})
  .fail(function (data) {
    m = data.responseJSON ? data.responseJSON.msg : "unknown";
    _show_message(m, "red");
  })
  .done(function (data) {
    build_result(data)
  });
}

function image_offset(value) {
  var site_index = parseInt($("[name=site_index]").val());
  if (site_index == 0 && value < 0) { return }
  $("[name=site_index]").val(site_index+value);
  load_images();
}

function build_result(data) {
  $("#result_space").text(data.files);
}