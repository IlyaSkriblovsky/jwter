$(document).on('click', '.folders-list-link', function () {
    var new_name = prompt('Переименовать папку', $(this).text())
    if (new_name)
    {
        $.post(URL.folder_rename($(this).attr('folder-id')), {
            csrfmiddlewaretoken: csrftoken,
            new_name: new_name
        })

        $(this).text(new_name)
    }

    return false
})

$(document).on('submit', '.folder-new-form', function () {
    var name = prompt('Новая папка')
    if (name)
        $(this).find('[name="name"]').val(name)
    else
        return false
})
