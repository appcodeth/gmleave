var app = angular.module('app', ['cgBusy']).config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('@{').endSymbol('}');
});

app.factory('factory', function($http) {
    var factory = {};

    factory.getReportList = function(approve) {
        return $http.get('/api/report/detail/?approve=' + approve);
    };

    return factory;
});

app.controller('ctrl', function($scope, $timeout, factory) {
    $scope.report_list = [];
    $scope.decimal_digits = 2;
    $scope.total_ot = 0;
    $scope.total_hours = 0;
    $scope.total_amount = 0;

    $scope.getReportList = function() {
        $scope.myPromise = factory.getReportList($('#approve').val());
        $scope.myPromise.then(function(res) {
            $scope.report_list = res.data.rows;
        });
    };

    $scope.$watch('report_list', function() {
        $scope.total_amount = 0;
        angular.forEach($scope.report_list, function(item) {
            $scope.total_amount += item.sum_amount;
            $scope.total_ot += item.rate;
            $scope.total_hours += item.sum_hours;
        });
    }, true);

    $scope.printExcel = function() {
        window.location.href = '/api/report/detail/xlsx/?approve=' + $('#approve').val();
    };

    $scope.init = function() {
        $scope.getReportList();
    };

    $scope.init();
});
