var Logs = new (class {
	constructor() {
		this.modal_id = "#log_modal";
		this.list_id = "#log_list";
		this.total_field_id = "#log_amount";
		this.phantom_class = ".log";
		this.track_list_id = "#log_track_list";
		this.track_phantom_class = ".track-option";

		this.default_limit = 50;
		this.default_page = 0;

		this.current_limit = 0;
		this.current_page = 0;
		this.current_max_page = 0;
	}

	show() {
		// loads in default values or taken from url
		let limit = DynamicURL.get("logs[limit]") || this.default_limit;
		let page = DynamicURL.get("logs[page]") || this.default_page;
		let date_from = DynamicURL.get("logs[page]") || "";
		let date_to = DynamicURL.get("logs[page]") || "";

		var req = {
			limit: limit,
			offset: (page * limit),
			date_from: date_from,
			date_to: date_to
		};

		this.loadTrackOptions();
		this.load( req );
	}

	load(x={}) {
		var LogsO = this;
		x["guild_id"] = $("#guild_id").val();

		$.get("/api/discord/logs/get", x)
		.done(function (data) {

			// update view
			LogsO.updatePageIndexButtons(data);

			var LogsList = $(LogsO.list_id).html("");
			$(LogsO.total_field_id).text(data.total);

			for (var log of data.result) {
				var Template = $(`[phantom] ${LogsO.phantom_class}`).clone();

				insertData(Template, log);
				Template.attr("log-id", log.log_id);

				LogsList.append(Template);
			}
		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"could not load logs"} );
		})
	}

	loadTrackOptions() {
		$.get("/api/discord/logs/list")
		.done(function (data) {

			var TrackList = $(`[location=logs] .controls [name=event_value]`).html("");

			TrackList.append( $("<option value='0'>All Events</option>") );
			for (var track_name in data.result) {
				let track_value = data.result[track_name];
				TrackList.append( $(`<option value='${track_value}'>${track_name}</option>`) );
			}
		});
	}

	// utils
	nextPage(last=false) {
		this.current_page += 1;
		if (last) { this.current_page = this.current_max_page; }

		var search = extractData("[location=logs] .controls");
		search["offset"] = (this.current_page * search["limit"]);
		this.load(search);
	}

	prevPage(first=false) {
		this.current_page -= 1;
		if (first) { this.current_page = 0; }

		var search = extractData("[location=logs] .controls");
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
			DynamicURL.set("logs[limit]", this.current_limit);
		} else {
			DynamicURL.set("logs[limit]", null);
		}

		// update page url if needed
		if (this.current_page != this.default_page) {
			DynamicURL.set("logs[page]", this.current_page);
		} else {
			DynamicURL.set("logs[page]", null);
		}

		// update html elements
		$("[location=logs] [name=limit]").val(this.current_limit);
		$("[location=logs] .pages .prev").attr("disabled", (this.current_page <= 0) );
		$("[location=logs] .pages .next").attr("disabled", (this.current_page >= this.current_max_page) );
		$("[location=logs] .pages .page").text(this.current_page+1);
	}

	// edit
	editModal() {
		// To display the current track state we require the discord settings and a list of all track options.
		var LogsO = this;
		var req = {
			"guild_id": $("#guild_id").val()
		};

		$.get("/api/discord/configs/get", req)
		.done(function (config_data) {
			$.get("/api/discord/logs/list")
			.done(function (track_data) {
				buildTrackModal(config_data, track_data);
			})
			.fail(function (data) {
				generalAPIErrorHandler( {data:data, msg:"could not load track options"} );
			});
		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"error loading track settings"} );
		});

		function buildTrackModal(config_data, track_data) {

			// that actully only selects the channel, but hey
			insertData(LogsO.modal_id, config_data.result);

			// build track options
			var current_track_config = config_data.result.track_value || 0;
			var TrackOptionList = $(LogsO.track_list_id).html('');

			for (var track_name in track_data.result) {
				var track_value = track_data.result[track_name];

				var NextTrackOption = $(`[phantom] ${LogsO.track_phantom_class}`).clone();

				NextTrackOption.find("[name=track_name]").text(track_name);
				NextTrackOption.find("[name=track_value]").val(track_value);
				if (current_track_config & track_value) {
					NextTrackOption.find("[name=is_enabled]").prop("checked", true);
				}
				TrackOptionList.append(NextTrackOption);
			}

			$(LogsO.modal_id).attr("mode", "edit");
			$(LogsO.modal_id).modal("show");
		}

	}

	edit() {
		var LogsO = this;

		var req = {};
		req["guild_id"] = $("#guild_id").val();
		req["track_channel"] = $(`${LogsO.modal_id} [name=track_channel]`).val();
		req["track_value"] = 0;

		$(`${LogsO.track_list_id} ${LogsO.track_phantom_class}`).each(function (x, Track) {
			Track = $(Track);
			if ( Track.find("[name=is_enabled]").is(":checked") ) {
				let v = parseInt( Track.find("[name=track_value]").val() );
				req["track_value"] = req["track_value"] | v;
			}
		})

		$.post("/api/discord/configs/edit", req)
		.done(function (data) {

			$(LogsO.modal_id).modal("hide");
			LogsO.show();
			Display.showMessage({content: data.msg, color:Display.color_success, time:1500});

		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"error updating logs"} );
		});
	}
});
