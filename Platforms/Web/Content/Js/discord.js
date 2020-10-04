function discordUserAvatar(member_id, avatar_hash, size=32) {
	if (avatar_hash) {
		return `https://cdn.discordapp.com/avatars/${member_id}/${avatar_hash}?size=${size}`;
	} else {
		let mem_pic = parseInt(member_id) % 5;
		return `https://cdn.discordapp.com/embed/avatars/${mem_pic}.png`;
	}
}

function discordGuildAvatar(guild_id, icon_hash, size=32) {
	if (guild_id) {
		return `https://cdn.discordapp.com/icons/${guild_id}/${icon_hash}?size=${size}`;
	} else {
		let gui_pic = parseInt(guild_id) % 5;
		return `https://cdn.discordapp.com/embed/avatars/${gui_pic}.png`;
	}
}

function discordTranslateRequire(level) {
	if (level == 0) { return "Everyone"; }
	if (level == 1) { return "Booster"; }
	if (level == 2) { return "Regulars"; }
	if (level == 3) { return "Moderators"; }
	if (level == 4) { return "Server Owner"; }
	if (level >= 5) { return "System"; }
}
