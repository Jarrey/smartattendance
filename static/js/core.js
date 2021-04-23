$(document).ready(function(){
    $('#date_range').datepicker({
        maxViewMode: 2,
        todayBtn: "linked",
        language: "zh-CN",
        daysOfWeekHighlighted: "0,6",
        todayHighlight: true,
        autoclose: true
    });
    var today = new Date();
    $('#from_date').datepicker('setDate', new Date(today.getFullYear(), today.getMonth(), 1));
    $('#to_date').datepicker('setDate', new Date(today.getFullYear(), today.getMonth() + 1, 0));

    $.get("attendance", function(d) {
        $("#data_area").val(d);
    });
});


// submit and general report
function submit() {
    var f_date = $('#from_date').datepicker('getDate');
    var t_date = $('#to_date').datepicker('getDate');
    var d = $("#data_area").val();
    $.ajax({
        url: 'attendance',
        type: 'post',
        contentType : 'application/json',
        xhrFields:{ responseType: 'blob' },
        data: JSON.stringify({from_date: moment(f_date).format('yyyyMMDD'), to_date: moment(t_date).format('yyyyMMDD'), data: d}),
        success: function(blob, status, xhr) {
            var filename = "";
            var disposition = xhr.getResponseHeader('Content-Disposition');
            if (disposition && disposition.indexOf('attachment') !== -1) {
                var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                var matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
                filename = decodeURIComponent(filename);
            }
            var URL = window.URL || window.webkitURL;
            var downloadUrl = URL.createObjectURL(blob);

            if (filename) {
                // use HTML5 a[download] attribute to specify filename
                var a = document.createElement("a");
                // safari doesn't support this yet
                if (typeof a.download === 'undefined') {
                    window.location.href = downloadUrl;
                } else {
                    a.href = downloadUrl;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                }
            } else {
                window.location.href = downloadUrl;
            }

            setTimeout(function () { URL.revokeObjectURL(downloadUrl); }, 100);
        }
    });
};