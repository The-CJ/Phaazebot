function ask_delete_custom_command(server_id, trigger) {
  var yes = confirm('Are you sure you want to delete: "'+trigger+'" ?');
  if (yes) {
    delete_custom_command(server_id, trigger)
    get_server_custom_commands(server_id);

  }
}