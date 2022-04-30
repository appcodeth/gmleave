$(function () {
    var date = new Date();
    var firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
    var lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);

    $('.from_date').datepicker({
        clearBtn: true,
        format: 'dd/mm/yyyy',
    }).datepicker('update', firstDay);

    $('.to_date').datepicker({
        clearBtn: true,
        format: 'dd/mm/yyyy',
    }).datepicker('update', lastDay);
});

function getDate(s) {
    var temps = s.split('/');
    return temps[2] + '-' + temps[1] + '-' + temps[0];
}

var app = angular.module('app', ['cgBusy']).config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('@{').endSymbol('}');
});

app.factory('factory', function($http) {
    var factory = {};

    factory.getReportList = function(start, end) {
        return $http.get('/api/report/list/?start=' + start + '&end=' + end);
    };

    return factory;
});

app.controller('ctrl', function($scope, $timeout, factory) {
    $scope.report_list = [];
    $scope.decimal_digits = 2;
    $scope.total_amount = 0;

    $scope.getReportList = function() {
        start = $('#from_date').val();
        end = $('#to_date').val();
        console.log(start, end);
        $scope.myPromise = factory.getReportList(getDate(start), getDate(end));
        $scope.myPromise.then(function(res) {
            $scope.report_list = res.data.rows;
        });
    };

    $scope.$watch('report_list', function() {
        $scope.total_amount = 0;
        angular.forEach($scope.report_list, function(item) {
            $scope.total_amount += item.ot_amount;
        });
    }, true);
});
