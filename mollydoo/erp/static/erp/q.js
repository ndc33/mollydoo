if (!$) {
    // Need this line because Django also provided jQuery and namespaced as django.jQuery
    $ = django.jQuery;
}

$(document).ready(function() {
    $("select[name='date_schedualed']").change(function() {
        $("select['confirmed']").val('False');
    });
});