function toggleConsole() {
	$('#root_console').collapse('toggle');
}

function evalCommand(x={}) {

	var ex = extractData("#root_console");

	x["command"] = x["command"] || ex["command"];
	x["corotine"] = x["corotine"] || ex["corotine"];

	$.post("/api/admin/evaluate", x)
		.done(function (data) {
			$("#result_data").text(data.result)
		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data} );
		})
}
