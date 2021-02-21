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

		$("[location=commands_help] [info-window]").hide();
		if ( isEmpty(func) ) {
			// nothing selected, enable placeholder
			$("[location=commands_help] [info-window=placeholder]").show();
			return;
		} else {
			$("[location=commands_help] [info-window=data]").show();
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
			$("[location=commands_help] [name=recommended_cooldown]").text(cmd.recommended_cooldown);
			$("[location=commands_help] [name=recommended_require]").text( discordTranslateRequire(cmd.recommended_require) );

			var ArgListRequire = $("[location=commands_help] [arg-list=require]").html('');
			var ArgListOptional = $("[location=commands_help] [arg-list=optional]").html('');
			var ExampleList = $("[location=commands_help] [example-list]").html('');

			// require
			for (var entry of cmd.required_arguments) {
				var Arg = $("<p></p>");
				Arg.text(entry);
				ArgListRequire.append(Arg);
			}

			// optional
			for (var entry of cmd.optional_arguments) {
				var Arg = $("<p></p>");
				Arg.text(entry);
				ArgListOptional.append(Arg);
			}

			// examples
			for (var entry of cmd.example_calls) {
				var Example = $("<p></p>");
				Example.text(entry);
				ExampleList.append(Example);
			}

			// endless
			if (cmd.endless_arguments) {
				$("[location=commands_help] [endless-args]").show();
			} else {
				$("[location=commands_help] [endless-args]").hide();
			}

			$("[location=commands_help] [content-type]").hide();
			if (cmd.need_content) {
				$("[location=commands_help] [content-type=need]").show();
			} else if (cmd.allows_content) {
				$("[location=commands_help] [content-type=allows]").show();
			} else {
				$("[location=commands_help] [content-type=none]").show();
			}



			console.log(cmd);

		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"Could not load command help"} );
		})

	}

});
