function discordUserAvatar(member_id, avatar_hash, size=32) {
  if (avatar_hash) {
    return "https://cdn.discordapp.com/avatars/"+member_id+"/"+avatar_hash+"?size="+size;
  } else {
    return "https://cdn.discordapp.com/embed/avatars/" + (parseInt(member_id) % 5) + ".png";
  }
}
