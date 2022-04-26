$(function() {
    var g_start_1 = moment().startOf('year');
    var g_end_1 = moment().endOf('year');

    function cb1(start, end) {
        $('#daterange1 span').html(start.format('DD/MM/YYYY') + ' - ' + end.format('DD/MM/YYYY'));
        g_start_1 = start.format('YYYY-MM-DD');
        g_end_1 = end.format('YYYY-MM-DD');
        select_ot_hours_chart();
    }

    $('#daterange1').daterangepicker({
        startDate: g_start_1,
        endDate: g_end_1,
        ranges: {
            'This Year': [moment().startOf('year'), moment().endOf('year')],
            'Last Year': [moment().subtract(1, 'year').startOf('year'), moment().subtract(1, 'year').endOf('year')],
        }
    }, cb1);
    cb1(g_start_1, g_end_1);

    function _render_ot_hours_chart_all() {
        $.ajax({
            url: '/api/dashboard/hours/all/',
            type: 'get',
            async: true,
            data: {
                'start': g_start_1,
                'end': g_end_1
            },
            success: function(res) {
                Highcharts.chart('bar-container1', {
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
                            'Jan',
                            'Feb',
                            'Mar',
                            'Apr',
                            'May',
                            'Jun',
                            'Jul',
                            'Aug',
                            'Sep',
                            'Oct',
                            'Nov',
                            'Dec',
                        ],
                        crosshair: true
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'OT (Hours)'
                        }
                    },
                    tooltip: {
                        headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                        pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}:</td><td style="padding:0"><b>{point.y:.1f} Hours</b></td></tr>',
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
                    series: res.rows,
                });
            },
            error: function(err) {
                console.log('Connect error!', err);
            }
        });
    }

    function _render_ot_hours_chart_by_employee() {
        $.ajax({
            url: '/api/dashboard/hours/employee/',
            type: 'get',
            async: true,
            data: {
                'start': g_start_1,
                'end': g_end_1
            },
            success: function(res) {
                Highcharts.chart('bar-container1', {
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
                            'Jan',
                            'Feb',
                            'Mar',
                            'Apr',
                            'May',
                            'Jun',
                            'Jul',
                            'Aug',
                            'Sep',
                            'Oct',
                            'Nov',
                            'Dec',
                        ],
                        crosshair: true
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'OT (Hours)'
                        }
                    },
                    tooltip: {
                        headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                        pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}:</td><td style="padding:0"><b>{point.y:.1f} Hours</b></td></tr>',
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
                    series: res.rows,
                });
            },
            error: function(err) {
                console.log('Connect error!', err);
            }
        });
    }

    function select_ot_hours_chart() {
        if ($('#filter1').val() == 'all') {
            _render_ot_hours_chart_all();
        } else {
            _render_ot_hours_chart_by_employee();
        }
    }

    $('#filter1').on('change', function() {
        select_ot_hours_chart();
    });

    /*******************************************************/
    var g_start_2 = moment().startOf('year');
    var g_end_2 = moment().endOf('year');

    function cb2(start, end) {
        $('#daterange2 span').html(start.format('DD/MM/YYYY') + ' - ' + end.format('DD/MM/YYYY'));
        g_start_2 = start.format('YYYY-MM-DD');
        g_end_2 = end.format('YYYY-MM-DD');
        select_ot_amount_chart();
    }

    $('#daterange2').daterangepicker({
        startDate: g_start_2,
        endDate: g_end_2,
        ranges: {
            'This Year': [moment().startOf('year'), moment().endOf('year')],
            'Last Year': [moment().subtract(1, 'year').startOf('year'), moment().subtract(1, 'year').endOf('year')],
        }
    }, cb2);
    cb2(g_start_2, g_end_2);

    function _render_ot_amount_chart_all() {
        $.ajax({
            url: '/api/dashboard/amount/all/',
            type: 'get',
            async: true,
            data: {
                'start': g_start_2,
                'end': g_end_2
            },
            success: function(res) {
                Highcharts.chart('bar-container2', {
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
                            'Jan',
                            'Feb',
                            'Mar',
                            'Apr',
                            'May',
                            'Jun',
                            'Jul',
                            'Aug',
                            'Sep',
                            'Oct',
                            'Nov',
                            'Dec',
                        ],
                        crosshair: true
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'OT Amount (Baht)'
                        }
                    },
                    tooltip: {
                        headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                        pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}:</td><td style="padding:0"><b>{point.y:.1f} Baht</b></td></tr>',
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
                    series: res.rows,
                });
            },
            error: function(err) {
                console.log('Connect error!', err);
            }
        });
    }

    function _render_ot_amount_chart_by_employee() {
        $.ajax({
            url: '/api/dashboard/amount/employee/',
            type: 'get',
            async: true,
            data: {
                'start': g_start_2,
                'end': g_end_2
            },
            success: function(res) {
                Highcharts.chart('bar-container2', {
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
                            'Jan',
                            'Feb',
                            'Mar',
                            'Apr',
                            'May',
                            'Jun',
                            'Jul',
                            'Aug',
                            'Sep',
                            'Oct',
                            'Nov',
                            'Dec',
                        ],
                        crosshair: true
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'OT Amount (Baht)'
                        }
                    },
                    tooltip: {
                        headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                        pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}:</td><td style="padding:0"><b>{point.y:.1f} Baht</b></td></tr>',
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
                    series: res.rows,
                });
            },
            error: function(err) {
                console.log('Connect error!', err);
            }
        });
    }

    function select_ot_amount_chart() {
        if ($('#filter2').val() == 'all') {
            _render_ot_amount_chart_all();
        } else {
            _render_ot_amount_chart_by_employee();
        }
    }

    $('#filter2').on('change', function() {
        select_ot_amount_chart();
    });

});

