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
    var year = $('#year').val();
    if (year);
    else {
        alert('Please select year');
        return;
    }

    var tr = '';
    $.ajax({
        url: '/api/report/leave/holiday?year=' + year,
        type: 'get',
        async: false,
        success: function (res) {
            var col_name = '';
            col_name += '<th class="text-center">วันที่</th>';
            col_name += '<th class="text-center">ถึงวันที่</th>';
            col_name += '<th>รายละเอียด</th>';
            table_result.append('<thead><tr>' + col_name + '</tr></thead>');

            $.each(res.rows, function (index, data) {
                var col_value = '';
                col_value += '<td class="text-center">' + (data.from_date) + '</td>';
                col_value += '<td class="text-center">' + (data.to_date) + '</td>';
                col_value += '<td>' + (data.name) + '</td>';
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
    var year = today.getFullYear();
    $('#year').val(year);
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
    var year = $('#year').val();
    if (year);
    else {
        alert('Please select year');
        return;
    }
    window.open('http://localhost:8080/birt/run?__report=holiday.rptdesign&__format=pdf&year=' + year, '_blank');
});

$('#btnRenderExcel').on('click', function() {
    var year = $('#year').val();
    if (year);
    else {
        alert('Please select year');
        return;
    }
    window.open('http://localhost:8080/birt/run?__report=holiday.rptdesign&__format=xlsx&year=' + year, '_blank');
});

$(function () {
    hideReport();
    getCurrentDate();
});
