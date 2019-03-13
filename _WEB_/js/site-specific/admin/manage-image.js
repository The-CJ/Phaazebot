$("document").ready(function () {
  load_images();
})

function load_images() {
  let search = $("[name=image_search]").val();
  $.get("/api/admin/manage-image/get", {image:search, limit: 30})
  .fail(function (data) {
    m = data.responseJSON ? data.responseJSON.msg : "unknown";
    _show_message(m, "red");
  })
  .done(function (data) {
    $("#result_space").text(data.files);
      console.log(data);
  });
}