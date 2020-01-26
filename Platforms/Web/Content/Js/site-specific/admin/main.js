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
      generalAPIErrorHandler( {data:data} );
    })
}
