$(document).on('click', '.folders-list-link', function () {
    var new_name = prompt('Переименовать папку', $(this).text())
    if (new_name)
    {
        var form = $(this).next('form')
        form.find('[name="new_name"]').val(new_name)
        form.submit()
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
