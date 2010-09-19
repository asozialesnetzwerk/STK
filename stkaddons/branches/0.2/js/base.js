function editOption(type, dest, option)
{
    header = "<form action=\"index.php?go=ajaxpost" + dest+"\" method=\"POST\">";
    footer = "<input type=\"submit\" /></form>";
    cancel = "<a class=\"back\" href=\"javascript:removeOption()\">Cancel</a>";
    if(type == "input")
    {
        $("#option_edit").html("<h3>" + dest + "</h3>" + header + "<input id=\"option_input\" name=\"option_input\" type=\"text\" />" + footer + cancel)
    }
    else if(type == "select")
    {
        $("#option_edit").html("<h3>" + dest + "</h3>" + header + "<select id=\"option_input\" name=\"option_input\" >" + option + "</select>" + footer + cancel)
    }
    else if (type == "textarea")
    {
    }
    else
    {
        $("#option_edit").html(type)
    }
    $("#option_edit").css("display", "block");
}
function removeOption()
{
    $("#option_edit").css("display", "none");
}
