var ConfigsChannel = new (class {
	constructor() {
		this.operation = null;
		this.modal_id = "#configs_channel_exeption_modal";
		this.list_id = "#exception_channel_list";
		this.phantom_class = ".exceptionchannel";
	}

	show() {
		this.load();
	}

	load(x={}) {
		x["guild_id"] = $("#guild_id").val();

		$.get("/api/discord/configs/get", x)
		.done(function (data) {

			// insert current data
			insertData("[location=configs_channel]", data.result);

		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"could not load configs for channel"} );
		})
	}

	getOptionDict(operation) {

		if (operation == "level") {
			return {
				"endpoint":"leveldisabledchannels",
				"modal_title":"Level disabled channels"
			}
		}

		if (operation == "normal") {
			return {
				"endpoint":"normaldisabledchannels",
				"modal_title":"Normal-Command disabled channels"
			}
		}

		if (operation == "regular") {
			return {
				"endpoint":"regulardisabledchannels",
				"modal_title":"Regular-Command disabled channels"
			}
		}

		if (operation == "quote") {
			return {
				"endpoint":"quotedisabledchannels",
				"modal_title":"Quote-Command disabled channels"
			}
		}

		if (operation == "game") {
			return {
				"endpoint":"gameenabledchannels",
				"modal_title":"Game-Command enabled channels"
			}
		}

		if (operation == "nsfw") {
			return {
				"endpoint":"nsfwenabledchannels",
				"modal_title":"NSFW-Command enabled channels"
			}
		}

		return {}

	}

	showChannelList(operation) {
		var ConfigsChannelO = this;
		var req = {};
		req["guild_id"] = $("#guild_id").val();

		var options = this.getOptionDict(operation);

		if (isEmpty(options)) { throw `can't resolve for operation: ${operation}`; }

		$.get(`/api/discord/configs/${options.endpoint}/get`, req)
		.done(function (data) {

			var EntryList = $(ConfigsChannelO.list_id).html('');
			for (var entry of data.result) {
				var channel = DiscordDashboard.getDiscordChannelByID(entry.channel_id);
				var Template = $(`[phantom] ${ConfigsChannelO.phantom_class}`).clone();
				Template.attr("entry-id", entry.entry_id);
				Template.find("[name=channel_name]").text( channel ? channel.name : "(DELETED CHANNEL)" );
				if (isEmpty(channel)) {
					Template.addClass("deleted");
					Template.attr("title", "This channel is deleted on the server and can be deleted here as well without any worries");
				}
				EntryList.append(Template);
			}

			// set stuff for later
			ConfigsChannelO.operation = operation;
			$(`${ConfigsChannelO.modal_id} [name=operation]`).val(operation);

			// set description
			$(`${ConfigsChannelO.modal_id} [modal-desc]`).hide();
			$(`${ConfigsChannelO.modal_id} [modal-desc=${operation}]`).show();

			// set title
			$(`${ConfigsChannelO.modal_id} .modal-title`).text(options.modal_title);

			// show modal
			$(ConfigsChannelO.modal_id).modal("show");
		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:`could not load configs for ${channel_list} channel exceptions`} );
		});
	}

	// create
	createChannelEntry() {
		var ConfigsChannelO = this;
		var req = {};
		req["guild_id"] = $("#guild_id").val();
		req["channel_id"] = $("#new_exceptionchannel").val();

		var operation = $(`${ConfigsChannelO.modal_id} [name=operation]`).val();

		if (operation != this.operation) {
			console.log("unequal operation stored, wtf");
			operation = this.operation;
		}

		var options = this.getOptionDict(operation);
		if (isEmpty(options)) { throw `can't resolve for operation: ${operation}`; }

		$.post(`/api/discord/configs/${options.endpoint}/create`, req)
		.done(function (data) {
			Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
			$("#new_exceptionchannel").val("");
			ConfigsChannelO.showChannelList(operation);
		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"error adding entry to list"} );
		});

	}

	// delete
	deleteChannelEntry(HTMLRow) {
		var ConfigsChannelO = this;
		var req = {};
		req["guild_id"] = $("#guild_id").val();
		req["entry_id"] = $(HTMLRow).closest(ConfigsChannelO.phantom_class).attr("entry-id");

		var operation = $(`${ConfigsChannelO.modal_id} [name=operation]`).val();

		if (operation != this.operation) {
			console.log("unequal operation stored, wtf");
			operation = this.operation;
		}

		var options = this.getOptionDict(operation);
		if (isEmpty(options)) { throw `can't resolve for operation: ${operation}`; }

		$.post(`/api/discord/configs/${options.endpoint}/delete`, req)
		.done(function (data) {
			Display.showMessage({content: data.msg, color:Display.color_success, time:1500});
			ConfigsChannelO.showChannelList(operation);
		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"error deleting entry from list"} );
		});

	}
});
