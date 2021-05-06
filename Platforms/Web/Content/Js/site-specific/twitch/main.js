
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
			console.log(data);
		});


}

$("document").ready(function () {

});