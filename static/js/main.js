var trs = []
var forms = []
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
    $("thead input:checkbox:checked").prop("disabled", true)
    trs = $("tbody input:checkbox:checked").map(function(){
        return $(this).parent().parent()
    }).get();
    trs.forEach(function(item, i, arr){
        form = $('#table-form').clone()
        $(form).show()
        id = $(item).find('input:checkbox:first').prop('value')
        $(form).prop('id', 'table-form-' + id)
        $(form).find('#id').text(id)
        tds = $(item).find('td').get()
        $(form).find('#add-topic').val($(tds[2]).text())
        $(form).find('#add-text').val($(tds[3]).text())
        forms.push(form)
        form = $(item).replaceWith(form)
    })
    $('#change-controls').show()
}

function accept_change() {
    hide_all()
    forms.forEach(function(form, i, arr){
        tr = trs[i]
        $(form).replaceWith(tr)
    })
    trs = []
    forms = []
    $("thead input:checkbox:checked").prop("disabled", false)
}

function decline_change() {
    hide_all()
    forms.forEach(function(form, i, arr){
        tr = trs[i]
        $(form).replaceWith(tr)
    })
    trs = []
    forms = []
    $("thead input:checkbox:checked").prop("disabled", false)
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

function scroll_bottom() {
  $("html, body").animate({ scrollTop: $(document).height()-$(window).height() }, "fast");
  return false;
};

function scroll_top() {
  $("html, body").animate({ scrollTop: 0}, "fast");
  return false;
};