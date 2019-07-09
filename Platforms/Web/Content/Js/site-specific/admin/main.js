function evalCommand(command) {
  if (command == null) {
    command = $('#eval_command').val();
  }
  var r = {
    command: command,
  };
  if ( $("[name=corotine]").is(":checked") ) { r["corotine"] = true; }
  $.post("/api/admin/evaluate", r)
    .done(function (data) {
      $("#result_data").text(data.result)
    })
    .fail(function (data) {
      let msg = data.responseJSON ? data.responseJSON.error : "unknown";
      Display.showMessage( {content:msg, color:Display.color_critical} );
    })
}
