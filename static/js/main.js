var trs = []
var forms = []
var table_form
var json = []
$(document).ready(function(){
    table_form = $('#table-form').clone()
});
function open_add() {
    hide_all()
    form = table_form
    $(form).prop('id', 'add-form')
    $('tbody').prepend(form)
    form.show()
    $('#add-controls').show()
}

function close_add() {
    hide_all()
}

function accept_add() {
    json = []
    id = $(form).find('#id').text()
    topic = $(form).find('#add-topic').val()
    text = $(form).find('#add-text').val()
    json.push({id: id, topic: topic, text: text })
    send(json, 'http://127.0.0.1:5000/quote/add')
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
        id = $(item).find('input:checkbox:first').prop('value')
        tds = $(item).find('td').get()
        $(form).prop('id', 'table-form-' + id)
        $(form).find('#id').text(id)
        $(form).find('#add-topic').val($(tds[2]).text())
        $(form).find('#add-text').val($(tds[3]).text())
        $(form).find('#add-img').prop('name', 'add-img-' + id)
        $(form).find('.upload-file-info').prop('id', 'info-add-img-' + id)
        $(form).show()
        forms.push(form)
        $(item).replaceWith(form)
    })
    $('#change-controls').show()
}

function accept_change() {
    json = []
    forms.forEach(function(form, i, arr){
        tr = trs[i]
        id = $(form).find('#id').text()
        topic = $(form).find('#add-topic').val()
        text = $(form).find('#add-text').val()
        json.push({id: id, topic: topic, text: text })
        $(form).replaceWith(tr)
    })
    trs = []
    forms = []
    $("thead input:checkbox:checked").prop("disabled", false)
    console.log(json)
    send(json, 'http://127.0.0.1:5000/quote/update')
    hide_all()
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

function accept_remove() {
    json = []
    trs = $("tbody input:checkbox:checked").map(function(){
            return $(this).parent().parent()
        }).get();
    trs.forEach(function(tr, i, arr) {
        json.push($(tr).find('input:checkbox:first').prop('value'))
    })
    send(json, 'http://127.0.0.1:5000/quote/delete')
}

function hide_all() {
    $('.controls-group').hide()
    $('#table-form').hide()
    $('#add-form').hide()
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

function send(data, url){
    console.log(JSON.stringify(data))
    $.ajax({
            url: url,
            type: 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            async: false,
            success: function(msg) {
                alert(msg);
            }
        });
}