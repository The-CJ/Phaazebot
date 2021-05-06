
function checkUserInput() {
	var search_for = $("#user_input_search").val();
	var req = {
		"term":"channel",
		"search":search_for,
	};
	$.get("/api/twitch/search", req)
		.done(function(data) {

		})
		.fail(function(data) {

		});


}

$("document").ready(function () {

});