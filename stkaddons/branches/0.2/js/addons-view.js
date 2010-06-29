function loadAddonsInformations(id)
{
    /* jquery function, see http://api.jquery.com/jQuery.ajax/*/
    $.ajax({
      url: "ajax.php?go=addons-view&value=" + id,
      /*FIXME : when the dev is finishd, we will be able to use the cache.*/
      cache: false,
      success: function(html){
        $("#viewAddons").html(html);
      }
});
}
