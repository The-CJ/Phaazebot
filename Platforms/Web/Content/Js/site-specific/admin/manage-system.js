$("document").ready(function () {
	AdminStatus.show();
})

var AdminStatus = new (class {
	constructor() {
		this.field_version = "#version";
		this.field_uptime = "#uptime";
		this.module_phantom_class = ".module";
	}

	show() {
		this.load();
	}

	load(x={}) {
		var AdminStatusO = this;

		$.get("/api/admin/status", x)
		.done(function (data) {
			$(AdminStatusO.field_version).text(data.result.version);

			AdminStatusO.buildUptime(data.result.uptime);
			AdminStatusO.buildModules(data.result.modules);
			AdminStatusO.buildDiscord(data.result.discord);
		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"loading status failed"} );
		});
	}

	// builder
	buildUptime(seconds) {
		// uptime
		let minutes = seconds / 60;
		let hours = minutes / 60
		seconds = seconds % 60
		minutes = minutes % 60
		$(this.field_uptime).text(parseInt(hours)+"h "+parseInt(minutes)+"m "+parseInt(seconds)+"s");
	}

	buildModules(modules) {
		var Target = $("[part=phaaze] [modules]");
		for (var module_name in modules) {
			var Template = $(`[phantom] ${this.module_phantom_class}`).clone();
			Template.attr("module", module_name);
			Template.find(".name").text(module_name);
			Template.find(".value").attr("active", modules[module_name] ? "true" : "false");
			Target.append(Template);
		}
	}

	buildDiscord(discord) {
		var Target = $("[part=discord]");
		insertData(Target, discord);
		Target.find("img").attr("src", discord.bot_avatar_url);
	}

	// utils
	changeModuleState(HTMLButton) {
		let active_str = $(HTMLButton).attr("active");
		let module_name = $(HTMLButton).closest(".module").attr("module");
		let module_state = (active_str == "true");

		// since we want to change the state, and the current state is a bool, we flip it
		var new_state = !module_state;
		let req = { module: module_name, state: new_state };

		$.post("/api/admin/module", req)
		.done(function (data) {
			$(`[part=phaaze] [modules] [module=${data.changed_module}] button.value`).attr("active", data.new_state);
			Display.showMessage( {content: data.msg, color:Display.color_success} );
		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"changing status failed"} );
		});
	}
});
