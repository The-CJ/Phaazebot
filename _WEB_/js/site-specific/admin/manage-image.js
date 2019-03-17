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

    //image_object.find("[edit]").attr("href", "/admin/manage-image/edit?edit="+image);

    image_object.find(".image-img").attr("src", "/img/"+image+"?sizeY=50");
    image_object.find(".image-img").attr("alt", "Image at: /img/"+image);
    rs.append(image_object);
  }
}

function delete_image(b) {
  var name = $(b).closest(".image-preview").find('.image-name').text();
  var e = confirm("sure you wanna delete: "+name);
  if (e) {
    $.post("/api/admin/manage-image/delete", {name:name})
    .done(function () {
      load_images();
    });
  }
}

function upload_image() {
  var name = $("#upload_modal [name=name]").val();
  if (name == "") { _show_message("Name can't be empty", "orange"); return; }
  var f = $("#upload_modal [name=file]");
  var r = {
    "name": name,
    "file": f[0].files[0],
  }
  var p = "/api/admin/manage-image/upload";
  function s(data) {
    _hide_loading();
    $("#upload_modal").modal('hide');
    _show_message(data.msg, "green");
  }
  function fa(data) {
    _hide_loading();
    _show_message(data.msg ? data.msg : "Critical Error", "red");
  }
  _show_loading("Uploading...");
  upload_file(r, p, s, fa);
}