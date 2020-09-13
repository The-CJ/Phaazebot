$("document").ready(function () {
	PublicCommands.show();
})

var PublicCommands = new (class {
	constructor() {
		this.modal_id = "#command_modal";
		this.list_id = "#command_list";
		this.total_amount_field = "#command_amount";
		this.phantom_class = ".command";

		this.default_limit = 50;
		this.default_page = 0;

		this.current_limit = 0;
		this.current_page = 0;
		this.current_max_page = 0;
	}

	show() {
		// loads in default values or taken from url
		let limit = DynamicURL.get("limit") || this.default_limit;
		let page = DynamicURL.get("page") || this.default_page;

		var req = {
			limit: limit,
			offset: (page * limit),
		};

		this.load(req);
	}

	load(x={}) {
		var PublicCommandsO = this;
		x["guild_id"] = $("#guild_id").val();

		$.get("/api/discord/commands/get", x)
		.done(function (data) {

			// update view
			PublicCommandsO.updatePageIndexButtons(data);

			$(PublicCommandsO.total_amount_field).text(data.total);
			var EntryList = $(PublicCommandsO.list_id).html("");

			for (var entry of data.result) {
				var Template = $(`[phantom] ${PublicCommandsO.phantom_class}`).clone();

				entry.require = discordTranslateRequire(entry.require);
				insertData(Template, entry);
				Template.attr("command-id", entry.command_id);

				if (entry.hidden) {
					Template.find("[name=name]").addClass("hidden");
					Template.find("[name=name]").attr("title", "Execute the command in the Discord server to see the result.");
				}
				EntryList.append(Template);
			}

		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"could not load commands"} );
		});
	}

	// utils
	nextPage(last=false) {
		this.current_page += 1;
		if (last) { this.current_page = this.current_max_page; }

		var search = extractData("main form.controls");
		search["offset"] = (this.current_page * search["limit"]);
		this.load(search);a
	}

	prevPage(first=false) {
		this.current_page -= 1;
		if (first) { this.current_page = 0; }

		var search = extractData("main form.controls");
		search["offset"] = (this.current_page * search["limit"]);
		this.load(search);
	}

	updatePageIndexButtons(data) {
		this.current_limit = data.limit;
		this.current_page = data.offset / data.limit;
		this.current_max_page = (data.total / data.limit);
		this.current_max_page = Math.ceil(this.current_max_page - 1)

		// update limit url if needed
		if (this.current_limit != this.default_limit) {
			DynamicURL.set("limit", this.current_limit);
		} else {
			DynamicURL.set("limit", null);
		}

		// update page url if needed
		if (this.current_page != this.default_page) {
			DynamicURL.set("page", this.current_page);
		} else {
			DynamicURL.set("page", null);
		}

		// update html elements
		$("main form.controls [name=limit]").val(this.current_limit);
		$("main form.controls .pages .prev").attr("disabled", (this.current_page <= 0) );
		$("main form.controls .pages .next").attr("disabled", (this.current_page >= this.current_max_page) );
		$("main form.controls .pages .page").text(this.current_page+1);
	}

	// edit
	editModal(HTMLButton) {
		var PublicCommandsO = this;
		var req = {
			"guild_id": $("#guild_id").val(),
			"command_id": $(HTMLButton).closest(PublicCommandsO.phantom_class).attr("command-id")
		};

		$.get("/api/discord/commands/get", req)
		.done(function (data) {
			var command = data.result.pop();

			let curr_single = $("#guild_currency").val();
			let curr_multi = $("#guild_currency_multi").val();
			command.cost = command.cost + ' ' + (command.cost == 1 ? curr_single : curr_multi);
			command.uses = `${command.uses} times`;
			command.require = discordTranslateRequire(command.require);
			if (command.hidden) {
				command.name = "(Hidden command)";
				command.description = "Execute this command in the Discord server to see the result.";
			}

			insertData(PublicCommandsO.modal_id, command);

			$(PublicCommandsO.modal_id).modal("show");
		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"could not load command detail"} );
		});
	}

});
