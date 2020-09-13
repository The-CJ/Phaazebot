var Admin = new (class {
	constructor() {
		this.console_wrap = "#root_console";
		this.console_output = "#console_output";
		this.console_trace = "#console_trace";
	}

	// utils
	toggleConsole() {
		$(this.console_wrap).collapse('toggle');
	}

	evalCommand(x={}) {
		var AdminO = this;
		var ex = extractData(this.console_wrap);

		$.post("/api/admin/evaluate", x)
		.done(function (data) {
			$(AdminO.console_output).text(data.result);
			$(AdminO.console_trace).text(data.traceback);
		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data} );
		});
	}

})
