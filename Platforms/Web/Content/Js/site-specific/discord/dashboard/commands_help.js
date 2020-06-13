var CommandsHelp = new (class {
  constructor() {

  }

  show() {
    this.load( {detailed: false} );
  }

  load(x={}) {
    var CommandsHelpO = this;

    $.get("/api/discord/commands/list", x)
    .done(function (data) {

      var HTMLSelect = $("[location=commands_help] [name=function]").html("");
      HTMLSelect.append( $("<option value=''>Please select a command...</option>") );

      for (var entry of data.result) {
        var Option = $("<option></option>");
        Option.attr("value", entry.function);
        Option.text(entry.name);
        HTMLSelect.append(Option);
      }

      CommandsHelpO.loadCommandInfo();

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"Could not load command help"} );
    })

  }

  // utils
  loadCommandInfo(func="") {

    if ( isEmpty(func) ) {
      // get value from select box
      func = $("[location=commands_help] [name=function]").val();
    }

    if ( isEmpty(func) ) {
      // loads in default values or taken from url
      func = DynamicURL.get("commands_help[func]");
    }

    if ( isEmpty(func) ) {
      // forget it
      return;
    }

    // reset in select, only needed if its set via preselect
    $("[location=commands_help] [name=function]").val(func);

    var req = {
      "function": func,
      "detailed": true,
      "recommended": true
    };

    $.get("/api/discord/commands/list", req)
    .done(function (data) {

      var cmd = data.result.pop();
      if ( isEmpty(cmd) ) { return; }

      DynamicURL.set("commands_help[func]", cmd.function);

      $("[location=commands_help] [name=name]").text(cmd.name);
      $("[location=commands_help] [name=description]").text(cmd.description);


    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"Could not load command help"} );
    })

  }

});
