$(document).ready(function(){
    $.get("date", function(d) {
        $("#holiday_area").val(d.holiday);
        $("#shiftday_area").val(d.shiftday);
    });
});

function save_day(day_type) {
    area = $("#" + day_type + "_area")
    $.ajax({
        url: 'date',
        type: 'post',
        contentType : 'application/json',
        data: JSON.stringify({type: day_type, data: area.val()}),
        success: function(d, s) {
            if(s == "success" && d == "OK") {
                alert("保存成功");
            }
        }
    });
};