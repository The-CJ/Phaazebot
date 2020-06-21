$("document").ready(function () {
  PublicQuotes.show();
})

var PublicQuotes = new (class {
  constructor() {
    this.list_id = "#quote_list";
    this.total_amount_field = "#quote_amount";
    this.phantom_class = ".quote";

  }

  show() {
    this.load();
  }

  load(x={}) {
    var PublicQuotesO = this;
    x["guild_id"] = $("#guild_id").val();

    $.get("/api/discord/quotes/get", x)
    .done(function (data) {

      $(PublicQuotesO.total_amount_field).text(data.total);
      var EntryList = $(PublicQuotesO.list_id).html("");

      for (var entry of data.result) {
        var Template = $(`[phantom] ${PublicQuotesO.phantom_class}`).clone();

        insertData(Template, entry);

        EntryList.append(Template);
      }

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load quotes"} );
    });
  }

  random() {
    this.load( {limit:1, random:true} );
  }

});
