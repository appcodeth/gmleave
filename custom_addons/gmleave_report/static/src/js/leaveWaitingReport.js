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
        url: '/api/report/leave/waiting?year=' + year,
        type: 'get',
        async: false,
        success: function (res) {
            var col_name = '';
            col_name += '<th class="text-center">รหัส</th>';
            col_name += '<th>ชื่อ-นามสกุล</th>';
            col_name += '<th>แผนก</th>';
            col_name += '<th>ตำแหน่ง</th>';
            col_name += '<th>ประเภท</th>';
            col_name += '<th class="text-center">เริ่มวันที่</th>';
            col_name += '<th class="text-center">ถึงวันที่</th>';
            col_name += '<th class="text-center">จำนวน (วัน)</th>';
            table_result.append('<thead><tr>' + col_name + '</tr></thead>');

            $.each(res.rows, function (index, data) {
                var col_value = '';
                col_value += '<td class="text-center">' + (data.code) + '</td>';
                col_value += '<td>' + (data.name) + '</td>';
                col_value += '<td>' + (data.position) + '</td>';
                col_value += '<td>' + (data.department) + '</td>';
                col_value += '<td>' + (data.leave_name) + '</td>';
                col_value += '<td class="text-center">' + (data.start_date) + '</td>';
                col_value += '<td class="text-center">' + (data.end_date) + '</td>';
                col_value += '<td class="text-center">' + (data.duration) + '</td>';
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
    window.open('http://157.230.255.67:8080/birt/run?__report=waiting_leave.rptdesign&__format=pdf&year=' + year, '_blank');
});

$('#btnRenderExcel').on('click', function() {
    var year = $('#year').val();
    if (year);
    else {
        alert('Please select year');
        return;
    }
    window.open('http://157.230.255.67:8080/birt/run?__report=waiting_leave.rptdesign&__format=xlsx&year=' + year, '_blank');
});

$(function () {
    hideReport();
    getCurrentDate();
});
