var Quotes = new (class {
  constructor() {
    this.amount = 0;
    this.temporarily_quote_content = {};
  }

  show(x={}) {
    var QuoteO = this;
    var guild_id = $("#guild_id").val();
    // var offset = x["offset"] ? x["offset"] : 0; // NOTE: do i need this?

    $.get("/api/discord/quotes/get", {guild_id: guild_id})
    .done(function (data) {

      QuoteO.amount = data.result.length;
      $("#quote_amount").text(QuoteO.amount);
      var QuoteList = $("#quote_list").html("");

      for (var quote of data.result) {
        var Template = $("[phantom] .quote").clone();

        // Template.find(".name").text( level.username );
        Template.find("[name=content]").val(quote.content);
        Template.find("[name=quote_id]").text(quote.quote_id);
        Template.attr("quote-id", quote.quote_id);

        QuoteList.append(Template);
      }

    })
    .fail(function (data) {
      generalAPIErrorHandler( {data:data, msg:"could not load quotes"} );
    })
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
