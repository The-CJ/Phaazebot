$("document").ready(function () {
  loadDiscordServers();
})

function loadDiscordServers() {

  $.get("/api/discord/guilds")
  .done(function (data) {
    for (guild of data.result) {
      var template = $("[phantom] .server").clone();
      var image_link = "https://cdn.discordapp.com/icons/{guild_id}/{icon}.png";
      var image_alt = "https://cdn.discordapp.com/embed/avatars/{icon}.png";

      var image = "";

      if (guild.icon) {
        image = image_link;
        image = image.replace("{guild_id}", guild.id);
        image = image.replace("{icon}", guild.icon);
      } else {
        let r = server.id % 5;
        image = image_alt;
        image = image.replace("{icon}", r);
      }

      template.find("img").attr("src", image);
      template.find(".name").text(guild.name);

      if (guild.manage) {
        $("#manageble_servers").append(template);
      } else {
        $("#viewable_servers").append(template);
      }

    }
  })
  .fail(function (data) {

  })

}
