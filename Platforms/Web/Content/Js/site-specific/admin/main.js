function evelCommand(command) {
  if (command == null) {
    command = $('#eval_command').val();
  }
  var r = {
    command: command
  };
  $.post("/api/admin/modules/evaluate", r)
    .done(function (data) {
      console.log(data);
    })
    .fail(function (data) {
      let msg = data.responseJSON ? data.responseJSON.error : "unknown";
      Display.showMessage( {content:msg, color:Display.color_critical} );
    })
}
