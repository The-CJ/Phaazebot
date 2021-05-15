
function checkUserInput() {
	var search_for = $("#user_input_search").val();
	var req = {
		"term": search_for,
		"search":"channel",
	};
	$.get("/api/twitch/search", req)
		.done(function(data) {
			$("#search_result_failed").hide();
			$("#search_result_success").show();
			var target_href = "/twitch/view/"+data.result.id;
			var anchor = $("#search_result_success_anchor");
			anchor.text(`${data.result.display_name + '\'s'} view page`);
			anchor.attr("href", target_href);
			window.location.href = target_href;
		})
		.fail(function(data) {
			$("#search_result_success").hide();
			$("#search_result_failed").show();
			setTimeout(
				() => { $("#search_result_failed").hide(); },
				20000
			);
		});


}

$("document").ready(function () {

});