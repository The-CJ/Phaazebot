function discordUserAvatar(member_id, avatar_hash, size=32) {
  if (avatar_hash) {
    return "https://cdn.discordapp.com/avatars/"+member_id+"/"+avatar_hash+"?size="+size;
  } else {
    return "https://cdn.discordapp.com/embed/avatars/" + (parseInt(member_id) % 5) + ".png";
  }
}

function discordTranslateRequire(level) {
  if (level == 0) { return "Everyone"; }
  if (level == 1) { return "Regulars"; }
  if (level == 2) { return "Moderators"; }
  if (level == 3) { return "Server Owner"; }
  if (level >= 4) { return "System"; }
}
