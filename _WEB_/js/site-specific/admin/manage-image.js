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
  var rs = $("#result_space").html("");
  for (image of data.files) {
    var image_object = $("[tpl] > .image-preview").clone();
    image_object.find(".image-name").text(image);
    image_object.find(".image-name").attr("href", "/img/"+image);
    image_object.find(".image-img").attr("src", "/img/"+image+"?sizeY=50");
    image_object.find(".image-img").attr("alt", "Image at: /img/"+image);
    rs.append(image_object);
  }
}