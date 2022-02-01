g_start_date1 = '';
g_end_date1 = '';

g_start_date2 = '';
g_end_date2 = '';

g_start_date3 = '';
g_end_date3 = '';

$(function () {
    var start = moment().startOf('year');
    var end = moment().endOf('year');

    //////////////////// default overview chart ///////////////////
    g_start_date1 = start.format('YYYY-MM-DD');
    g_end_date1 = end.format('YYYY-MM-DD');

    g_start_date2 = start.format('YYYY-MM-DD');
    g_end_date2 = end.format('YYYY-MM-DD');

    g_start_date3 = start.format('YYYY-MM-DD');
    g_end_date3 = end.format('YYYY-MM-DD');


    $('#overview_type').on('change', function () {
        select_overview_chart();
    });

    $('#personal_type').on('change', function () {
        select_personal_type_chart();
    });

    //////////////////// date range pickers ///////////////////

    //
    // datepicker
    //
    function cb(start, end, range) {
        $('#reportrange span').html('ช่วง ' + start.format('DD/MM/YYYY') + ' ถึง ' + end.format('DD/MM/YYYY'));
        if (range && range != 'Custom Range') {
            $('#reportrange span').html(range || 'เลือก');
        }

        g_start_date1 = start.format('YYYY-MM-DD');
        g_end_date1 = end.format('YYYY-MM-DD');
        select_overview_chart();
    }

    $('#reportrange').daterangepicker({
        startDate: start,
        endDate: end,
        ranges: {
            'ปีนี้': [moment().startOf('year'), moment().endOf('year')],
            'ปีที่แล้ว': [moment().subtract(1, 'year').startOf('year'), moment().subtract(1, 'year').endOf('year')],
        }
    }, cb);
    cb(start, end, 'ปีนี้');

    //
    // datepicker1
    //
    function cb1(start, end, range) {
        $('#reportrange1 span').html('ช่วง ' + start.format('DD/MM/YYYY') + ' ถึง ' + end.format('DD/MM/YYYY'));
        if (range && range != 'Custom Range') {
            $('#reportrange1 span').html(range || 'เลือก');
        }

        g_start_date2 = start.format('YYYY-MM-DD');
        g_end_date2 = end.format('YYYY-MM-DD');
        get_chart_ratio_pie();
    }

    $('#reportrange1').daterangepicker({
        startDate: start,
        endDate: end,
        ranges: {
            'ปีนี้': [moment().startOf('year'), moment().endOf('year')],
            'ปีที่แล้ว': [moment().subtract(1, 'year').startOf('year'), moment().subtract(1, 'year').endOf('year')],
        }
    }, cb1);
    cb1(start, end, 'ปีนี้');

    //
    // datepicker2
    //
    function cb2(start, end, range) {
        $('#reportrange2 span').html('ช่วง ' + start.format('DD/MM/YYYY') + ' ถึง ' + end.format('DD/MM/YYYY'));
        if (range && range != 'Custom Range') {
            $('#reportrange2 span').html(range || 'เลือก');
        }

        g_start_date3 = start.format('YYYY-MM-DD');
        g_end_date3 = end.format('YYYY-MM-DD');
        select_personal_type_chart();
    }

    $('#reportrange2').daterangepicker({
        startDate: start,
        endDate: end,
        ranges: {
            'ปีนี้': [moment().startOf('year'), moment().endOf('year')],
            'ปีที่แล้ว': [moment().subtract(1, 'year').startOf('year'), moment().subtract(1, 'year').endOf('year')],
        }
    }, cb2);
    cb2(start, end, 'ปีนี้');
});


// highcharts
////////////////////////////////////////////////////////////////////////////////////////////////
function get_chart_overview_all() {
    $.ajax({
        url: '/api/dashboard/overviewAll',
        type: 'get',
        async: true,
        data: {
            'start': g_start_date1,
            'end': g_end_date1
        },
        success: function (res) {
            Highcharts.chart('bar-container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: ''
                },
                subtitle: {
                    text: ''
                },
                xAxis: {
                    categories: [
                        'ม.ค.',
                        'ก.พ.',
                        'มี.ค.',
                        'เม.ย.',
                        'พ.ค.',
                        'มิ.ย.',
                        'ก.ค.',
                        'ส.ค.',
                        'ก.ย.',
                        'ต.ค.',
                        'พ.ย.',
                        'ธ.ค.'
                    ],
                    crosshair: true
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'จำนวนวันลา (วัน)'
                    }
                },
                tooltip: {
                    headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                    pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}:</td><td style="padding:0"><b>{point.y:.1f} วัน</b></td></tr>',
                    footerFormat: '</table>',
                    shared: true,
                    useHTML: true
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0
                    }
                },
                series: res.rows
            });
        },
        error: function (err) {
            console.log('Connect error!', err);
        }
    });
}

function get_chart_overview_by_type() {
    $.ajax({
        url: '/api/dashboard/overviewByType',
        type: 'get',
        data: {
            'start': g_start_date1,
            'end': g_end_date1
        },
        async: true,
        success: function (res) {
            Highcharts.chart('bar-container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: ''
                },
                subtitle: {
                    text: ''
                },
                xAxis: {
                    categories: [
                        'ม.ค.',
                        'ก.พ.',
                        'มี.ค.',
                        'เม.ย.',
                        'พ.ค.',
                        'มิ.ย.',
                        'ก.ค.',
                        'ส.ค.',
                        'ก.ย.',
                        'ต.ค.',
                        'พ.ย.',
                        'ธ.ค.'
                    ],
                    crosshair: true
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'จำนวนวันลา (วัน)'
                    }
                },
                tooltip: {
                    headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                    pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}:</td><td style="padding:0"><b>{point.y:.1f} วัน</b></td></tr>',
                    footerFormat: '</table>',
                    shared: true,
                    useHTML: true
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0
                    }
                },
                series: res.rows
            });
        },
        error: function (err) {
            console.log('Connect error!', err);
        }
    });
}

// select overview chart by type
function select_overview_chart() {
    if ($('#overview_type').val() == 'all') {
        get_chart_overview_all();
    } else {
        get_chart_overview_by_type();
    }
}


////////////////////////////////////////////////////////////////////////////////////////////////
function get_chart_ratio_pie() {
    $.ajax({
        url: '/api/dashboard/leaveRatioPie',
        type: 'get',
        data: {
            'start': g_start_date2,
            'end': g_end_date2
        },
        async: true,
        success: function (res) {
            Highcharts.chart('pie-container', {
                chart: {
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false,
                    type: 'pie'
                },
                title: {
                    text: ''
                },
                tooltip: {
                    pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
                },
                accessibility: {
                    point: {
                        valueSuffix: '%'
                    }
                },
                plotOptions: {
                    pie: {
                        cursor: 'pointer',
                        dataLabels: {}
                    }
                },
                series: [{
                    name: 'สัดส่วน',
                    colorByPoint: true,
                    data: res.rows,
                }]
            });
        },
        error: function (err) {
            console.log('Connect error!', err);
        }
    });
}


////////////////////////////////////////////////////////////////

function get_chart_personal_by_type() {
    $.ajax({
        url: '/api/dashboard/leavePersonalType',
        type: 'get',
        data: {
            'start': g_start_date3,
            'end': g_end_date3
        },
        async: true,
        success: function (res) {
            Highcharts.chart('person-container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: ''
                },
                subtitle: {
                    text: ''
                },
                xAxis: {
                    categories: res.columns,
                    crosshair: true
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'จำนวนวันลา (วัน)'
                    }
                },
                tooltip: {
                    headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                    pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}:</td><td style="padding:0"><b>{point.y:.1f} วัน</b></td></tr>',
                    footerFormat: '</table>',
                    shared: true,
                    useHTML: true
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0
                    }
                },
                series: res.rows
            });
        },
        error: function (err) {
            console.log('Connect error!', err);
        }
    });
}

function get_chart_personal_all() {
    $.ajax({
        url: '/api/dashboard/leavePersonalAll',
        type: 'get',
        data: {
            'start': g_start_date3,
            'end': g_end_date3
        },
        async: true,
        success: function (res) {
            Highcharts.chart('person-container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: ''
                },
                subtitle: {
                    text: ''
                },
                xAxis: {
                    categories: res.columns,
                    crosshair: true
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'จำนวนวันลา (วัน)'
                    }
                },
                tooltip: {
                    headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                    pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}:</td><td style="padding:0"><b>{point.y:.1f} วัน</b></td></tr>',
                    footerFormat: '</table>',
                    shared: true,
                    useHTML: true
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0
                    }
                },
                series: res.rows
            });
        },
        error: function (err) {
            console.log('Connect error!', err);
        }
    });
}

// select overview chart by personal
function select_personal_type_chart() {
    if ($('#personal_type').val() == 'all') {
        get_chart_personal_all();
    } else {
        get_chart_personal_by_type();
    }
}


////////////////////////////////////////////////////////////////

function gotoMenu(id) {
    $.get('/api/getmenu?model_id=gmleave.leave&menu_name=Leave', function (res) {
        if (res.menu_id) {
            window.location.href = '/web#view_type=form&model=gmleave.leave&menu_id=' + res.menu_id + '&action=' + res.action_id + '&id=' + id;
        } else {
            alert('Can not link menu!!');
        }
    });
}


// get leave list
var table_result = $('#table-approve');
var beginHtml = table_result.html();

function runLeaveList() {
    table_result.html('');
    table_result.append(beginHtml);
    table_result.hide();

    var tr = '';
    $.ajax({
        url: '/api/dashboard/approveList',
        type: 'get',
        async: true,
        success: function (res) {
            $('#data-count').html('(' + res.rows.length + ')');
            $.each(res.rows, function (index, data) {
                tr += '<tr>' +
                    '<td>' + data.name + '</td>' +
                    '<td>' + (data.duration || '') + '</td>' +
                    '<td><a href="javascript:gotoMenu(' + data.id + ')" class="btn btn-success">เปิดดู</a></td>' +
                '</tr>';
            });
            table_result.append('<tbody>' + tr + '</tbody>');
            table_result.show();
        },
        error: function (err) {
            console.log('Connect error!', err);
        }
    });
}

runLeaveList();


///////////////////////////////////////////////////////////

function numberWithCommas(num) {
    if (!num)
        return 0;
    return num.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function numberWithCommas(num, digits) {
    if (!num)
        return 0;
    return num.toFixed(digits).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// counter report
function runReport() {
    $.ajax({
        url: '/api/dashboard/count',
        type: 'get',
        async: true,
        success: function (res) {
            $.each(res.rows, function (index, data) {
                $('#count-all').html(numberWithCommas(data.count_all,0));
                $('#count-approve').html(numberWithCommas(data.count_approve,0));
                $('#count-cancel').html(numberWithCommas(data.count_cancel,0));
                $('#count-employee').html(numberWithCommas(data.count_employee,0));
            });
        },
        error: function (err) {
            console.log('Connect error!', err);
        }
    });
}

runReport();
