function editOption(type, dest, option)
{
    header = "<form action=\"javascript:validOption(" + dest + ")\"></form>";
    footer = "<input type=\"submit\" /></form>";
    if(type == "input")
    {
        $("#option_edit").html(header + "<h3>" + option + "</h3><input id=\"option_input\" type=\"text\" />" + footer)
        $("#option_edit").css("display", "block");
    }
    else if (type == "textarea")
    {
    }
    else
    {
        $("#option_edit").html(type)
    }
}
