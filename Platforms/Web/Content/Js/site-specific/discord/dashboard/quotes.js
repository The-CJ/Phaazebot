var Quotes = new (class {
  constructor() {
    this.default_limit = 10;
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
      offset: (page * limit)
    };

    this.load( req );
  }

  load(x={}) {
    var QuoteO = this;
    x["guild_id"] = $("#guild_id").val();

    $.get("/api/discord/quotes/get", x)
    .done(function (data) {

      // update view
      QuoteO.updatePageIndexButtons(data);

      var QuoteList = $("#quote_list").html("");
      $("#quote_amount").text(data.total);

      for (var quote of data.result) {
        var Template = $("[phantom] .quote").clone();

        if (quote.content.length > 100) {
          quote.content = quote.content.slice(0, 97) + "...";
        }

        insertData(Template, quote);
        Template.attr("quote-id", quote.quote_id);

        QuoteList.append(Template);
      }
    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load quotes"} );
    })
  }

  nextPage(last=false) {
    this.current_page += 1;
    var search = extractData("[location=quotes] .controlls");
    search["offset"] = (this.current_page * search["limit"]);
    this.load(search);
  }

  prevPage(first=false) {
    this.current_page -= 1;
    if (first) { this.current_page = 0; }

    var search = extractData("[location=quotes] .controlls");
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
    $("[location=quotes] [name=limit]").val(this.current_limit);
    $("[location=quotes] .pages .prev").attr("disabled", (this.current_page <= 0) );
    $("[location=quotes] .pages .next").attr("disabled", (this.current_page >= this.current_max_page) );

  }




  startEdit(HTMLButton) {
    var Quote = $(HTMLButton).closest(".quote");

    // stage content ins temp.
    var quote_id = Quote.attr("quote-id");
    var quote_content = Quote.find("[name=content]").val();
    this.temporarily_quote_content[quote_id] = quote_content;

    // hide controll group 1
    Quote.find(".controls.one").hide();

    // show control group 2 and make text field editable
    Quote.find(".controls.two").show();
    Quote.find("[name=content]").attr("readonly", null);
  }

  endEdit(HTMLButton) {
    var Quote = $(HTMLButton).closest(".quote");

    // edit is ended without save, restore old content
    var quote_id = Quote.attr("quote-id");
    var content = this.temporarily_quote_content[quote_id];
    if (!isEmpty(content)) {
      Quote.find("[name=content]").val(content);
      delete this.temporarily_quote_content[quote_id];
    }

    // hide controll group 2
    Quote.find(".controls.two").hide();

    // show control group 1 and make text field uneditable
    Quote.find(".controls.one").show();
    Quote.find("[name=content]").attr("readonly", true);
  }

  startDelete(HTMLButton) {
    var c = confirm("Are you sure you want to delete this quote?");
    if (!c) {return;}

    var Quote = $(HTMLButton).closest(".quote");
    var QuoteO = this;

    var guild_id = $("#guild_id").val();
    var quote_id = Quote.attr("quote-id");

    var req = {
      "guild_id": guild_id,
      "quote_id": quote_id
    };

    $.post("/api/discord/quotes/delete", req)
    .done(function (data) {

      QuoteO.amount -= 1;
      $("#quote_amount").text(QuoteO.amount);
      Quote.remove();
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error deleting quote"} );
    })
  }

  startSave(HTMLButton) {
    var Quote = $(HTMLButton).closest(".quote");

    // get all vars
    var guild_id = $("#guild_id").val();
    var quote_id = Quote.attr("quote-id");
    var quote_content = Quote.find("[name=content]").val();

    var req = {
      "guild_id": guild_id,
      "quote_id": quote_id,
      "content": quote_content
    };

    $.post("/api/discord/quotes/edit", req)
    .done(function (data) {

      Quote.find(".controls.one").show();
      Quote.find("[name=content]").attr("readonly", true);
      Quote.find(".controls.two").hide();
      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error updating quote"} );
    })
  }

  startNewModal() {
    $("#quote_modal_new").modal("show");
  }

  startNew() {

    var QuoteO = this;
    var req = extractData("#quote_modal_new");
    req["guild_id"] = $("#guild_id").val();

    $.post("/api/discord/quotes/create", req)
    .done(function (data) {

      Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
      $("#quote_modal_new").modal("hide");
      QuoteO.show();

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"error updating quote"} );
    })
  }
});
