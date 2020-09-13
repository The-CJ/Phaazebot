var Quotes = new (class {
	constructor() {
		this.modal_id = "#quote_modal";
		this.list_id = "#quote_list";
		this.total_field_id = "#quote_amount";
		this.phantom_class = ".quote";

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

			var QuoteList = $(QuoteO.list_id).html("");
			$(QuoteO.total_field_id).text(data.total);

			for (var quote of data.result) {
				var Template = $(`[phantom] ${QuoteO.phantom_class}`).clone();

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

	// utils
	nextPage(last=false) {
		this.current_page += 1;
		if (last) { this.current_page = this.current_max_page; }

		var search = extractData("[location=quotes] .controls");
		search["offset"] = (this.current_page * search["limit"]);
		this.load(search);
	}

	prevPage(first=false) {
		this.current_page -= 1;
		if (first) { this.current_page = 0; }

		var search = extractData("[location=quotes] .controls");
		search["offset"] = (this.current_page * search["limit"]);
		this.load(search);
	}

	updatePageIndexButtons(data) {
		this.current_limit = data.limit;
		this.current_page = data.offset / data.limit;
		this.current_max_page = (data.total / data.limit);
		this.current_max_page = Math.ceil(this.current_max_page - 1);

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
		$("[location=quotes] .pages .page").text(this.current_page+1);

	}

	// create
	createModal() {
		resetInput(this.modal_id);
		$(this.modal_id).attr("mode", "create");
		$(this.modal_id).modal("show");
	}

	create() {
		var QuoteO = this;
		var req = extractData(this.modal_id);
		req["guild_id"] = $("#guild_id").val();

		$.post("/api/discord/quotes/create", req)
		.done(function (data) {

			Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
			$(QuoteO.modal_id).modal("hide");
			QuoteO.show();

		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"error creating quote"} );
		})
	}

	// edit
	editModal(HTMLButton) {
		var QuoteO = this;

		var req = {
			"guild_id": $("#guild_id").val(),
			"quote_id": $(HTMLButton).closest(QuoteO.phantom_class).attr("quote-id")
		};
		$.get("/api/discord/quotes/get", req)
		.done(function (data) {

			var quote = data.result.pop();
			insertData(QuoteO.modal_id, quote);
			$(QuoteO.modal_id).attr("mode", "edit");
			$(QuoteO.modal_id).modal("show");

		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"error displaying quote"} );
		})
	}

	edit() {
		var QuoteO = this;

		var req = extractData(this.modal_id);
		req["guild_id"] = $("#guild_id").val();

		$.post("/api/discord/quotes/edit", req)
		.done(function (data) {

			$(QuoteO.modal_id).modal("hide");
			QuoteO.show();
			Display.showMessage({content: data.msg, color:Display.color_success, time:1500});

		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"error updating quote"} );
		})
	}

	// delete
	deleteFromList(HTMLButton) {
		let quote_id = $(HTMLButton).closest(this.phantom_class).attr("quote-id");
		this.delete(quote_id);
	}

	deleteFromModal() {
		let quote_id = $(`${this.modal_id} [name=quote_id]`).val();
		this.delete(quote_id);
	}

	delete(quote_id) {
		var c = confirm("Are you sure you want to delete this quote?");
		if (!c) {return;}

		var QuoteO = this;

		var req = {
			"guild_id": $("#guild_id").val(),
			"quote_id": quote_id
		};

		$.post("/api/discord/quotes/delete", req)
		.done(function (data) {
			$(QuoteO.modal_id).modal("hide");
			QuoteO.show();
			Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"error deleting quote"} );
		})
	}

});
