$("document").ready(function () {
  PublicQuotes.show();
})

var PublicQuotes = new (class {
  constructor() {
    this.list_id = "#quote_list";
    this.total_amount_field = "#quote_amount";
    this.phantom_class = ".quote";

    this.default_limit = 50;
    this.default_page = 0;

    this.current_limit = 0;
    this.current_page = 0;
    this.current_max_page = 0;
  }

  show() {
    // loads in default values or taken from url
    let limit = DynamicURL.get("quotes[limit]") || this.default_limit;
    let page = DynamicURL.get("quotes[page]") || this.default_page;

    var req = {
      limit: limit,
      offset: (page * limit),
    };

    this.load(req);
  }

  load(x={}) {
    var PublicQuotesO = this;
    x["guild_id"] = $("#guild_id").val();

    $.get("/api/discord/quotes/get", x)
    .done(function (data) {

      // update view
      PublicQuotesO.updatePageIndexButtons(data);

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

  // utils
  nextPage(last=false) {
    this.current_page += 1;
    var search = extractData("main form.controlls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  prevPage(first=false) {
    this.current_page -= 1;
    if (first) { this.current_page = 0; }

    var search = extractData("main form.controlls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  updatePageIndexButtons(data) {
    this.current_limit = data.limit;
    this.current_page = data.offset / data.limit;
    this.current_max_page = (data.total / data.limit);
    this.current_max_page = parseInt(this.current_max_page)

    // update limit url if needed
    if (this.current_limit != this.default_limit) {
      DynamicURL.set("quotes[limit]", this.current_limit);
    } else {
      DynamicURL.set("quotes[limit]", null);
    }

    // update page url if needed
    if (this.current_page != this.default_page) {
      DynamicURL.set("quotes[page]", this.current_page);
    } else {
      DynamicURL.set("quotes[page]", null);
    }

    // update html elements
    $("main form.controlls [name=limit]").val(this.current_limit);
    $("main form.controlls .pages .prev").attr("disabled", (this.current_page <= 0) );
    $("main form.controlls .pages .next").attr("disabled", (this.current_page >= this.current_max_page) );
    $("main form.controlls .pages .page").text(this.current_page+1);
  }

});
