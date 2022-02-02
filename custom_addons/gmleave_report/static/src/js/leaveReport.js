var table_result = $('#table-report');
var panel_result = $('#panel-report');
var beginHtml = table_result.html();

function hideReport() {
    table_result.hide();
    panel_result.hide();
}

function showReport() {
    table_result.show();
    panel_result.show();
}

function runReport() {
    var str_start = $('#start_date').val();
    var str_end = $('#end_date').val();

    if (str_start && str_end);
    else {
        alert('Please select date');
        return;
    }

    var start_date = getDate(str_start);
    var end_date = getDate(str_end);
    var tr = '';
    $.ajax({
        url: '/api/report/leave/personal?start_date=' + start_date + '&end_date=' + end_date,
        type: 'get',
        async: false,
        success: function (res) {
            var col_name = '';
            col_name += '<th class="text-center">รหัส</th>';
            col_name += '<th>ชื่อ-นามสกุล</th>';
            col_name += '<th>แผนก</th>';
            col_name += '<th>ตำแหน่ง</th>';
            $.each(res.columns, function(idx, col) {
                col_name += '<th class="text-center">' + col + '</th>';
            });
            col_name += '<th class="text-center">รวม</th>';
            table_result.append('<thead><tr>' + col_name + '</tr></thead>');

            $.each(res.rows, function (index, data) {
                var col_value = '';
                col_value += '<td class="text-center">' + (data.code) + '</td>';
                col_value += '<td>' + (data.name) + '</td>';
                col_value += '<td>' + (data.position) + '</td>';
                col_value += '<td>' + (data.department) + '</td>';

                var total_row = 0;
                $.each(res.columns, function(idx, col) {
                    col_value += '<td class="text-center">' + data[col] + '</td>';
                    total_row += parseFloat(data[col], 10);
                });
                col_value += '<td class="text-center">' + (total_row) + '</td>';

                tr += '<tr>' + col_value + '</tr>';
            });

            table_result.append('<tbody>' + tr + '</tbody>');
            showReport();
        },
        error: function (err) {
            console.log('Connect error!', err);
        }
    });
}

function getCurrentDate() {
    var today = new Date();

    var day = twoDigitsNumber(1);
    var month = twoDigitsNumber(today.getMonth() + 1);
    var year = today.getFullYear();
    var last_day = twoDigitsNumber(getLastDay(year, today.getMonth()));

    $('#start_date').val(day + '/' + month + '/' + year);
    $('#end_date').val(last_day + '/' + month + '/' + year);
}

$('#btnClearReport').on('click', function () {
    table_result.html('');
    table_result.append(beginHtml);
    hideReport();
    getCurrentDate();
    runReport();
});

$('#btnShowReport').on('click', function () {
    table_result.html('');
    table_result.append(beginHtml);
    hideReport();
    runReport();
});

$('#btnRenderPDF').on('click', function() {
    var str_start = $('#start_date').val();
    var str_end = $('#end_date').val();

    if (str_start && str_end);
    else {
        alert('Please select date');
        return;
    }

    var start_date = getDate(str_start);
    var end_date = getDate(str_end);
    window.open('http://157.230.255.67:8080/birt/run?__report=leave_by_personal.rptdesign&__format=pdf&start_date=' + start_date + '&end_date=' + end_date, '_blank');
});

$('#btnRenderExcel').on('click', function() {
    var str_start = $('#start_date').val();
    var str_end = $('#end_date').val();

    if (str_start && str_end);
    else {
        alert('Please select date');
        return;
    }

    var start_date = getDate(str_start);
    var end_date = getDate(str_end);
    window.open('http://157.230.255.67:8080/birt/run?__report=leave_by_personal.rptdesign&__format=xlsx&start_date=' + start_date + '&end_date=' + end_date, '_blank');
});


$(function () {
    $('.datepicker').datepicker({
        language: 'th',
        orientation: 'auto bottom',
        format: 'dd/mm/yyyy',
        todayHighlight: true,
    });

    hideReport();
    getCurrentDate();
});
