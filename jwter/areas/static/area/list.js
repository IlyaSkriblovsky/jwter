$(document).on('click', '.move-all-form .folder-menu-item, .move-form .folder-menu-item', function () {
    if ($(this).parent().hasClass('disabled'))
        return false

    var form = $(this).closest('form')
    form.find('[name="to"]').val($(this).attr('folder-id'))
    form.submit()
    return false
})
