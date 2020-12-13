// form management
function resetInput(o) {
	// o = JQuery object | str

	// 'o' is the target, in which all [name] elements get looped
	// and filled with a "neutral" state,
	// means empty strings in input fields and unchecked checkboxes

	// checkbox can be overwritten by [checked]
	// input fields can be overwritten by there [value] attribute
	// does not edit <data> elements!
	if (typeof o != "object") { o = $(o); }
	for (var f of o.find('[name]')) {
		f = $(f);

		// ignore data elements
		if ( f.is("data") ) { continue; }

		// is checkbox
		if (f.attr("type") == "checkbox") {
			f.prop( "checked", (f.is("[checked]") ? true : false) );
		}
		// any other type of element
		else {
			var pre_val = f.attr("value");
			f.val( pre_val ? pre_val : "" );
		}
	}
}

function extractData(o) {
	// o = JQuery object | str

	// 'o' is the target, in which all [name] elements get looped
	// and there .val() is stored with there attr('name') as this key
	// multiple same names overwrite each other, last one counts

	// if element is [type=checkbox] then data[name],
	// is 0 or 1 based on checked prop
	if (typeof o != "object") { o = $(o); }
	let data = {};
	for (var f of o.find('[name]')) {
		f = $(f);
		let name = f.attr('name');
		if (f.attr("type") == "checkbox") {
			if (f.is(":checked")) { data[name] = 1; }
			else { data[name] = 0; }
		}
		else {
			let value = f.val();
			data[name] = value;
		}
	}
	return data;
}

function insertData(Obj, data, to_string=false) {
	// obj = JQuery object | str
	// data = object
	// to_string = bool :: false

	// 'obj' is the target, in this target all keys of 'data' get searched
	// every matching [name=key] element, it inserts data[key]

	// if matching element is a [type=checkbox]:
	// element gets prop 'checked' set based on boolish interpretion of data[key]

	// if matching element is a SPAN
	// the value of data[key] gets inserted as text

	// to_string ensures content input by all types, except 'null'
	// which will be convertet to a empty string

	if (typeof Obj != "object") { Obj = $(Obj); }
	for (var key in data) {
		try {
			var value = data[key];

			// ensure stings?
			if (to_string) {
				if (typeof value == "boolean") { value = (value ? "true" : "false"); }
				else if (value == null) { value = ""; }
			}

			// find all elements based on [name]
			for (var Match of Obj.find(`[name=${key}]`)) {
				Match = $(Match);

				// checkboxes
				if (Match.attr("type") == "checkbox") {
					let checked = ( value ? true : false );
					Match.prop("checked", checked);
					continue;
				}

				if ( ["SPAN"].indexOf(Match.prop("tagName")) >= 0 ) {
					Match.text(value);
					continue;
				}

				Match.val(value);
				continue;
			}
		}
		catch (e) { continue }
	}
}

// general utils
function oppositeValue(v) {
	if (typeof v == "object") { throw "can't switch object type"; }
	else if (typeof v == "boolean") { return !v }
	else if (typeof v == "number") { return v * -1 }
	else if (typeof v == "string") {
		// if string, interpret values for a bool type
		// the strings "0", "false" and "" are often used to represent a false statement, so return true
		if (v == "0" || v == "false" || !v) { return true; }
		// everything else is true in string language
		else { return false; }
	}
	else {
		throw "unknown object handler";
	}

}

function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

function isEmpty(o) {
	// null
	if (o == null) { return true; }
	// string
	if (typeof o == "string") { if (o != "") { return false; } }
	// number
	if (typeof o == "number") { if (o != 0) { return false; } }
	// object
	for (var v in o) {
		if (o.hasOwnProperty(v)) {
			return false
		}
	}
	return true;
}

function showEmail(copy=false) {
	// i do this, so spam bots don't get the email from the site so easy

	var email = ["admin","@", "pha", "aze", ".", "net"].join("");

	if (copy) { return copyToClipboard(email); }

	$("#email_icon").popover({
		content: email,
		placement:"bottom",
		trigger:"hover"
	}).popover()
}

// user in-/out- puts
function copyToClipboard(content) {
	var TextA = $('<textarea>');
	TextA.val(content);
	TextA.attr("readonly", true);
	TextA.attr("style", "position:absolute; left: -10000px;");
	document.body.appendChild(TextA[0]);
	TextA[0].select();
	document.execCommand("copy");
	document.body.removeChild(TextA[0]);
}

// request handler
function formUpdate(x={}) {
	// this is like a extended version of JQuerys $.get or $post
	// if can be used like any other {key: value} request,
	// but this one supports File object and some other classes in the value spot

	var url = x["url"] ? x["url"] : "";
	var method = x["method"] ? x["method"] : "POST";
	var data = x["data"] ? x["data"] : {};
	var done_function = x["done_function"] ? x["done_function"] : function (x) {};
	var fail_function = x["fail_function"] ? x["fail_function"] : function (x) {};

	var RequestHandler = new XMLHttpRequest();
	var RequestForm = new FormData();

	for (var key in data) {
		let value = data[key];
		RequestForm.append(key, value);
	}

	RequestHandler.onreadystatechange= function () {
		if (this.readyState != 4) { return; }
		var content_type = this.getResponseHeader("content-type") || "";

		var final_response = this.responseText;
		if (content_type.startsWith("application/json")) { final_response = JSON.parse(final_response); }

		if (200 <= this.status && this.status <= 299) {
			done_function(final_response);
		} else if (300 <= this.status && this.status <= 399) {
			console.log("mm yes good question, we got a 300 <= X <= 399");
		} else if (400 <= this.status && this.status <= 599) {
			fail_function(final_response);
		}
	}

	RequestHandler.open(method, url);
	RequestHandler.send(RequestForm);

}

function generalAPIErrorHandler(x={}) {
	// it does what you whould think it does,
	// give this function the data object from a $.get .post .etc...
	// and it will give you a display message,
	// with the message, or at least the error... mostly
	// also sends stuff to debug log

	// message content priority
	// server message -> alternativ message -> server error code -> "Unknown"

	// x : data :: jquery response
	// x : msg :: str
	// x : color :: str ::: Display.color_info
	// x : time :: int ::: Display.default_time.
	// x : no_message :: bool ::: false

	var data = x["data"] ? x["data"] : null;
	var color = x["color"] ? x["color"] : Display.color_critical;
	var time = x["time"] ? x["time"] : Display.default_time;
	var alt_msg = x["msg"] ? x["msg"] : null;

	// most likely alwys is true, since this is a ERROR function
	if (data.responseJSON) { data = data.responseJSON; }

	var final_message = null;

	// server gave us a 'msg'
	if (data.msg) { final_message = data.msg; }
	// server has not 'msg' but user gave one
	else if (alt_msg) { final_message = alt_msg; }
	// no 'msg' at all take server 'error'
	else if (alt_msg) { final_message = data.error; }
	// no 'msg' or 'error'... means "unknown"
	else { final_message = "Unknown error"; }

	if (!x["no_message"]) {
		// console.log({content:final_message, color:color, time:time});
		Display.showMessage( {content:final_message, color:color, time:time} );
	}
	console.log(data);
}

function hrefLocation(x={}) {
	// this function can be applied to pretty much all elements
	// and make it so if has the same functionallity than a anchor <a> element
	// its recommended to use it via: onmousedown
	// the target value is only for left clicks and will be overwritten when middle mouse is pressed
	// giving 'middle' or 'left' a false value will disable this clicktype for the the event

	// x : href :: str
	// x : target :: str ::: "_self"
	// x : left :: bool ::: true
	// x : middle :: bool ::: true

	var href = x["href"] ? x["href"] : null;
	var target = x["target"] ? x["target"] : "_self";
	var left = x["left"] ? x["left"] : true;
	var middle = x["middle"] ? x["middle"] : true;

	if (isEmpty(href)) { throw "missing href"; }
	if (event.button == undefined) { throw "could not find pressed button"; }

	// this is the so called Cheese, so we can click a anchor
	var Anchor = document.createElement('a');
	Anchor.href = href;
	Anchor.target = target;

	// primary or left click
	if (left && event.button === 0) {
		let PrimaryClick = new MouseEvent( "click", {button:0, buttons:1, which:1} );
		return Anchor.dispatchEvent( PrimaryClick );
	}

	// middle mouse click
	if (middle && event.button === 1) {
		Anchor.target = "_blank";
		let AuxClick = new MouseEvent( "click", {button:1, buttons:4, which:2 } );
		return Anchor.dispatchEvent( AuxClick );
	}

}

// big classes
var SessionManager = new (class {
	constructor() {
		this.modal_id = "#account_modal";
	}

	showAccountPanel(field="select") {
		// hiding everything
		$(`${this.modal_id}[mode] [show-mode]`).hide();
		$(`${this.modal_id}[mode] [show-mode] [login]`).hide();

		// show selected field and the login loading
		$(`${this.modal_id}[mode] [show-mode=${field}]`).show();
		$(`${this.modal_id}[mode] [show-mode=${field}] [login=loading]`).show();
		$(this.modal_id).modal('show');

		if (field != "select") { this.getAccountInfo(field); }
	}

	getAccountInfo(platform) {
		var SessionManagerO = this;
		var url = "/api/account";

		if (platform == "phaaze") { url = "/api/account/phaaze/get"; }
		if (platform == "discord") { url = "/api/account/discord/get"; }
		if (platform == "twitch") { url = "/api/account/twitch/get"; }
		if (platform == "osu") { url = "/api/account/osu/get"; }

		$.get(url)
		.done(function (data) {
			SessionManagerO.displayInfo(platform, data.user);
		})
		.fail(function (data) {
			// only do additional handling if its not a 401, because getting a unauthorised is actully pretty normal for a login question
			if (data.status != 401) { generalAPIErrorHandler( {data:data, msg:`Could not load info for platform: ${platform}`} ); }

			// hide the login attributes and show login = false
			$(`${SessionManagerO.modal_id} [show-mode=${platform}] [login]`).hide();
			$(`${SessionManagerO.modal_id} [show-mode=${platform}] [login=false]`).show();
		});
	}

	displayInfo(platform, data) {
		if (platform == "phaaze") {
			insertData(`${this.modal_id} [show-mode=phaaze] [login=true]`, data);
			var RoleList = $(`${this.modal_id} [show-mode=phaaze] [login=true] [user-role-list]`).html("");
			for (var role of data.roles) {
				RoleList.append( $("<div class='role'>").text(role) );
			}
		}

		if (platform == "discord") {
			$(`${this.modal_id} [show-mode=discord] [login=true] [name=current_discord_username]`).val(data.username);
			let avatar = discordUserAvatar(data.user_id, data.avatar, 256);
			$(`${this.modal_id} [show-mode=discord] [login=true] [name=current_discord_avatar]`).attr("src", avatar);
		}

		if (platform == "twitch") {
			$(`${this.modal_id} [show-mode=twitch] [login=true] [name=current_twitch_username]`).val(data.display_name);
			$(`${this.modal_id} [show-mode=twitch] [login=true] [name=current_twitch_avatar]`).attr("src", data.profile_image_url);
		}

		// hide the login attributes and show login = true
		$(`${this.modal_id} [show-mode=${platform}] [login]`).hide();
		$(`${this.modal_id} [show-mode=${platform}] [login=true]`).show();
	}

	login() {
		var SessionManagerO = this;
		var login_data = extractData(`${SessionManagerO.modal_id} [show-mode=phaaze] [login=false]`);
		$.post("/api/account/phaaze/login", login_data)
		.done(function (data) {
			CookieManager.set("phaaze_session", data.phaaze_session, data.expires_in);
			Display.showMessage({'content': 'You successfull logged in!' ,'color':Display.color_success});
			$(SessionManagerO.modal_id).modal('hide');
		})
		.fail(function (data) {
			var user = $(`${SessionManagerO.modal_id} [show-mode=phaaze] [login=false] [name=username]`).addClass("animated shake");
			var pass = $(`${SessionManagerO.modal_id} [show-mode=phaaze] [login=false] [name=password]`).addClass("animated shake").val("");
			setTimeout(function () {
				user.removeClass("animated shake");
				pass.removeClass("animated shake");
			}, 1000);
		})
	}

	logout(platform) {
		var SessionManagerO = this;
		var url = "/api/account";

		if (platform == "phaaze") { url = "/api/account/phaaze/logout"; }
		if (platform == "discord") { url = "/api/account/discord/logout"; }
		if (platform == "twitch") { url = "/api/account/twitch/logout"; }
		if (platform == "osu") { url = "/api/account/osu/logout"; }

		$.post(url)
		.done(function (data) {
			Display.showMessage({"content": `You successfull logged out from ${platform}`,'color':Display.color_success});
			if (platform == "phaaze") { CookieManager.remove("phaaze_session"); }
			if (platform == "discord") { CookieManager.remove("phaaze_discord_session"); }
			if (platform == "twitch") { CookieManager.remove("phaaze_twitch_session"); }
			$(SessionManagerO.modal_id).modal('hide');
		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"Unable to logout"} );
		});
	}

	edit() {
		var SessionManagerO = this;
		var data = extractData(`${SessionManagerO.modal_id} [show-mode=phaaze] [login=true]`);
		$.post("/api/account/phaaze/edit", data)
		.done(function (data) {
			Display.showMessage({content:data.msg, color:Display.color_success});
		})
		.fail(function (data) {
			generalAPIErrorHandler( {data:data, msg:"Editing failed."} );
		})
	}
})()

var CookieManager = new (class {
	constructor() {

	}

	get(cookie) {
		var name = cname + "=";
		var decodedCookie = decodeURIComponent(document.cookie);
		var ca = decodedCookie.split(';');
		for(var i = 0; i <ca.length; i++) {
				var c = ca[i];
				while (c.charAt(0) == ' ') {
						c = c.substring(1);
				}
				if (c.indexOf(name) == 0) {
						return c.substring(name.length, c.length);
				}
		}
		return "";
	}

	set(name, value, expires_in) {
		if (expires_in == null) {
			document.cookie = name+'='+value+'; Path=/';
		}
		else {
			document.cookie = name+'='+value+'; Max-Age=' + expires_in + '; Path=/';
		}
	}

	remove(name) {
		document.cookie = name+"=; Max-Age=-1; Path=/"
	}
})()

var Display = new (class {
	constructor() {
		this.color_success = "#38ca35";
		this.color_warning = "#e7b23c";
		this.color_critical = "#e83d3d";
		this.color_info = "#4285FF";
		this.default_time = 10000;
		this.loading_tag_name = "__loading__screen__";
	}

	showMessage(m) {
		if (m == null) { throw "missing message"; }
		if (m.content == null) { throw "missing message content"; }
		if (m.time == null) { m.time = this.default_time; }
		if (m.color == null) { m.color = this.color_info; }
		if (m.text_color == null) { m.text_color = "#fff"; }

		// the main display field is located in the navbar, so its everywere.
		var messagebox = $('[messagebox]');

		var mid = (Math.floor(Math.random()*1000000));
		var message = $('<div class="message" onclick="$(this).remove()"><h1></h1></div>');
		message.attr("mid", mid);
		message.css("animation-duration", m.time+"ms");
		var messagebar_raw = $('<div class="messagebar_raw"></div>');
		var messagebar_time_left = $('<div class="messagebar_time_left"></div>');
		messagebar_time_left.css("animation-duration", m.time+"ms");

		// build message
		message.find("h1").text(m.content);
		messagebar_raw.append(messagebar_time_left);
		message.append(messagebar_raw);

		// add style
		message.css('background', m.color);
		message.css('color', m.text_color);

		// append and start remove timer
		messagebox.append(message);

		setTimeout(
			function () { $('[messagebox] > [mid='+mid+']').remove(); },
			m.time
		);
	}

	loadingScreen(state, message="Loading...") {
		var FoundScreens = $(`[name=${this.loading_tag_name}]`);
		if (!state) { FoundScreens.remove(); }
		else {
			if (FoundScreens.length != 0) { return; /* there are already some active*/ }

			var LoadingScreen = $("<div/>");
			LoadingScreen.attr("class", "center-item-row");
			LoadingScreen.attr("name", this.loading_tag_name);

			var LoadingScreenInner = $("<div/>");
			LoadingScreenInner.attr("class", "center-item-col w-100");

			LoadingScreen.append(LoadingScreenInner);

			// img
			let Img = $("<img>");
			Img.attr("src", "/img/favicon.ico");
			Img.attr("alt", "logo");
			Img.attr("class", "animation-spin");
			LoadingScreenInner.append(Img);

			// msg
			let Msg = $("<h1>");
			Msg.text(message);
			Msg.attr("class", "text-white");
			LoadingScreenInner.append(Msg);

			// disable click
			LoadingScreen.attr("onclick", "Display.loadingScreen(false);");
			$("body").prepend(LoadingScreen);
		}

	}

})

var DynamicURL = new (class {
	constructor() {
		this.values = this.getAll();
	}

	set(key, value, update=true) {
		this.values[key] = value;
		if (update) { this.update(); }
	}

	get(key) {
		let value = this.values[key];
		if (value == null) {
			value = this.getFromLocation(key);
			this.values[key] = value;
		}
		return value
	}

	getAll() {
		var search = location.search.substring(1);
		search = search.replace(/&/g, '","');
		search = search.replace(/=/g, '":"');

		if (isEmpty(search)) { return {}; }

		try {
			return JSON.parse( `{"${search}"}`,
				function(key, value) { return (key==="") ? value : decodeURIComponent(value); }
			)
		} catch (e) {
			return {};
		}

	}

	update() {
		let ucurl = window.location.pathname;
		let pre = "?";

		for (var key in this.values) {
			let value = this.values[key];
			if (isEmpty(value)) { continue; }

			ucurl = ucurl + pre + key + "=" + encodeURIComponent(value);
			pre = "&";

		}
		window.history.replaceState('obj', 'newtitle', ucurl);
	}

	getFromLocation(name) {
		let url = window.location.href;
		name = name.replace(/[\[\]]/g, '\\$&');
		var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
				results = regex.exec(url);
		if (!results) return null;
		if (!results[2]) return '';
		return decodeURIComponent(results[2].replace(/\+/g, ' '));
	}

})

// load finished, add events
$("document").ready(function () {

})
