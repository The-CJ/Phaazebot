
function checkUserInput() {
	var search_for = $("#user_input_search").val();
	var req = {
		"term": search_for,
		"search":"channel",
	};
	$.get("/api/twitch/search", req)
		.done(function(data) {
			console.log(data);
		})
		.fail(function(data) {
			$("#search_result_failed").show();
			setTimeout(
				() => { $("#search_result_failed").hide(); },
				20000
			);
		});


}

$("document").ready(function () {

});