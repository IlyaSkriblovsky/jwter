ymaps.ready(function () {
    $('.ymap').each(function () {
        var form = $(this).closest('form')
        var x    = form.find('[name="x"]')
        var y    = form.find('[name="y"]')
        var zoom = form.find('[name="zoom"]')

        var map = new ymaps.Map(this, {
            type: 'yandex#map',
            center: [ x.val(), y.val() ],
            zoom: zoom.val(),

            behaviors: [ 'default', 'scrollZoom' ]
        })
        $(this).data('map', map)

        map.events.add('boundschange', function (event) {
            x.val(event.get('newCenter')[0])
            y.val(event.get('newCenter')[1])
            zoom.val(event.get('newZoom'))
        })


        var marks_text = form.find('[name="marks"]').val()
        var marks = marks_text.split(',')
        for (var i = 0; i < marks.length; i++)
        {
            var parts = marks[i].split('|')
            switch (parts[0])
            {
                case 'Circle':
                    var bounds = [
                        [ parseFloat(parts[1]), parseFloat(parts[2]) ],
                        [ parseFloat(parts[3]), parseFloat(parts[4]) ]
                    ]
                    var diameter = map.options.get('projection').getCoordSystem().getDistance(
                        [ bounds[0][0], bounds[0][1] ],
                        [ bounds[1][0], bounds[0][1] ]
                    )
                    map.geoObjects.add(new ymaps.Circle(
                        [
                            [
                                (bounds[0][0] + bounds[1][0]) / 2,
                                (bounds[0][1] + bounds[1][1]) / 2
                            ],
                            diameter / 2
                        ],
                        {},
                        obj_options
                    ))
                    break

                case 'Polygon':
                    map.geoObjects.add(new ymaps.Polygon(
                        ymaps.geometry.Polygon.fromEncodedCoordinates(parts[1]),
                        {},
                        obj_options
                    ))
                    break
            }
        }
    })
})

$(document).on('click', '.search-button', function () {
    var form = $(this).closest('form')
    var query = form.find('[name="address"]').val().trim()

    var mapcontainer = form.find('.ymap')
    var map = mapcontainer.data('map')

    if (! query) return false


    ymaps.geocode(query, {
        boundedBy: map.getBounds(),
        results: 1
    }).then(
        function (result) {
            var obj = result.geoObjects.getIterator().getNext()

            if (obj)
            {
                var bounds = obj.geometry.getBounds()
                var centerAndZoom = ymaps.util.bounds.getCenterAndZoom(bounds, [mapcontainer.width(), mapcontainer.height()])

                map.setCenter(centerAndZoom.center)
                map.setZoom(Math.min(centerAndZoom.zoom, 16))
            }
            else
                alert('Адрес не найден')
        }
    )

    return false
})


obj_options = {
    draggable: true,

    fillColor: '0066ff33',

    strokeWidth: 2
}



$(document).on('click', '.polygon', function () {
    var mapcontainer = $(this).closest('form').find('.ymap')
    var map = mapcontainer.data('map')

    var polygon = new ymaps.Polygon([[]], {}, obj_options)
    map.geoObjects.add(polygon)
    polygon.editor.startDrawing()

    $(this).closest('form').find('.polygon-edit').addClass('btn-info')

    return false
})
$(document).on('click', '.polygon-edit', function () {
    $(this).toggleClass('btn-info')

    var mapcontainer = $(this).closest('form').find('.ymap')
    var map = mapcontainer.data('map')

    var enable = $(this).hasClass('btn-info')

    map.geoObjects.each(function (obj) {
        if (obj.editor)
        {
            if (enable)
                obj.editor.startEditing()
            else
                obj.editor.stopEditing()
        }
    })

    return false
})


$(document).on('click', '.circle', function () {
    var mapcontainer = $(this).closest('form').find('.ymap')
    var map = mapcontainer.data('map')

    map.geoObjects.each(function (obj) {
        if (obj.geometry.getType() == 'Circle')
            map.geoObjects.remove(obj)
    })

    var circle = new ymaps.Circle([
        map.getCenter(), $(this).closest('form').find('.radius-slider').slider('value')
    ], {}, obj_options)
    map.geoObjects.add(circle)

    return false
})


$(function () {
    $('.radius-slider')
        .slider({
            min: 10,
            max: 100,
            value: 25
        })
        .on('slide', function (ev, ui) {
            var mapcontainer = $(this).closest('form').find('.ymap')
            var map = mapcontainer.data('map')

            map.geoObjects.each(function (obj) {
                if (obj.geometry.getType() == 'Circle')
                    obj.geometry.setRadius(ui.value)
            })
        })
})


$(document).on('click', '.clear', function () {
    var mapcontainer = $(this).closest('form').find('.ymap')
    var map = mapcontainer.data('map')

    map.geoObjects.each(function (obj) {
        map.geoObjects.remove(obj)
    })

    return false
})



$(function () {
    $('.ymap').each(function () {
        $(this).closest('form').on('submit', function () {
            var parts = []
            $(this).find('.ymap').data('map').geoObjects.each(function (obj) {
                var geo = obj.geometry
                switch (geo.getType())
                {
                    case 'Circle':
                        var bounds = geo.getBounds()
                        var numbers = [bounds[0][0], bounds[0][1], bounds[1][0], bounds[1][1]]
                        var strings = $.map(numbers, function (n) { return n.toFixed(6).toString() })
                        parts.push('Circle|' + strings.join('|'))
                        break
                    case 'Polygon':
                        var coords = geo.getCoordinates()
                        for (var i = coords.length - 1; i >= 0; i--)
                        {
                            if (coords[i].length < 4) // Minimum vertex number is 4: triangle + 1 for duplicating first and last vertices as YMaps do
                            {
                                geo.splice(i, 1)
                            }
                        }
                        if (geo.getCoordinates().length > 0)
                            parts.push('Polygon|' + ymaps.geometry.Polygon.toEncodedCoordinates(geo))
                        break
                }
            })

            $(this).find('[name="marks"]').val(parts.join(','))
        })
    })
})



$(document).on('click', '.restore-menu-item', function () {
    var form = $(this).closest('form')
    form.find('[name="restore_to"]').val($(this).attr('folder-id'))
    form.submit()
    return false
})
