var trs = [];
function open_add() {
    hide_all()
    $('#table-form').show()
    $('#add-controls').show()
}

function close_add() {
    hide_all()
}

function open_change() {
    hide_all()
    trs = $(".table input:checkbox:checked").map(function(){
        return $(this).parent().parent()
    }).get();
    trs.forEach(function(item, i, arr){
        $(item).addClass('selected')
        form = $('#table-form').show()
        form
        form = $(item).replaceWith(form)
    })
    console.log(trs)
    $('#change-controls').show()
}

function accept_change() {
    hide_all()
    console.log(trs)
    trs.forEach(function(item, i, arr){
        $(item).val().removeClass('selected')
    })
}

function open_remove() {
    hide_all()
    $('#remove-controls').show()
}

function close_remove() {
    hide_all()
}

function hide_all() {
    $('.controls-group').hide()
    $('#table-form').hide()
}

function trigger_checks(elem) {
    $(':checkbox').prop( "checked", $(elem).prop('checked') );
}