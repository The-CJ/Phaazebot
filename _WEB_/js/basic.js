$('.expandable_button').hover(
  function () {
    $(this).find('span.expandable_content').addClass("open_collapsed_button");
  },
  function () {
    $(this).find('span.expandable_content').removeClass("open_collapsed_button");
  }
);