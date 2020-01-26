$("document").ready(function () {
  loadDiscordServers();
})

function loadDiscordServers() {

  $.get("/api/discord/userguilds")
  .done(function (data) {
    for (guild of data.result) {
      var template = $("[phantom] .guild").clone();
      var image_link = "https://cdn.discordapp.com/icons/{guild_id}/{icon}.png";
      var image_alt = "https://cdn.discordapp.com/embed/avatars/{icon}.png";

      var image = "";

      if (guild.icon) {
        image = image_link;
        image = image.replace("{guild_id}", guild.id);
        image = image.replace("{icon}", guild.icon);
      } else {
        let r = guild.id % 5;
        image = image_alt;
        image = image.replace("{icon}", r);
      }

      template.find("img").attr("src", image);
      template.attr("title", guild.name);
      template.find(".name").text(guild.name);
      template.find('a').attr("href", template.find('a').attr("href").replace("{server_id}", guild.id));

      if (guild.manage) {
        $("#manageble_servers").append(template);
      } else {
        $("#viewable_servers").append(template);
      }

    }
  })
  .fail(function (data) {
    generalAPIErrorHandler( {data:data, msg:"could not load your Discord guilds"} );
  })

}
