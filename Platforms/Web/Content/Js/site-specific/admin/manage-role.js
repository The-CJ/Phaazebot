$("document").ready(function () {
  getRoles();
})

function getRoles() {
  $.get("/api/admin/roles/get")
  .done(function (data) {

    console.log(data);

  })
  .fail(function (data) {
    let msg = data.responseJSON ? data.responseJSON.error : "unknown";
    Display.showMessage( {content:msg, color:Display.color_critical} );
    console.log(data);
  })
}
