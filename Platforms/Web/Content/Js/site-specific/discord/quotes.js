$("document").ready(function () {
  loadQuotes();
})

function loadQuotes() {

  var guild_id = $("#guild_id").val();

  $.get("/api/discord/quotes/get", {guild_id: guild_id})
  .done(function (data) {

    $("#quote_amount").text(data.result.length);
    var QuoteList = $("#quote_list").html("");

    for (var quote of data.result) {
      var Template = $("[phantom] .quote").clone();

      Template.find("[name=quote_id]").text(quote.quote_id);
      Template.find("[name=content]").val(quote.content);

      QuoteList.append(Template);
    }

  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"could not load quotes"} );
  })
}
