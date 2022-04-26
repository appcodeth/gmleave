function calculateOTAmount(salary, cfg_workday_per_month, cfg_workhour_per_day, ot_rate, actual_work_hours) {
    return (salary / cfg_workday_per_month / cfg_workhour_per_day) * ot_rate * actual_work_hours;
}

var app = angular.module('app', ['cgBusy']).config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('@{').endSymbol('}');
});

app.factory('factory', function($http) {
    var factory = {};

    factory.getOTEmployeeList = function() {
        return $http.get('/api/ot/employee/list/');
    };

    factory.getOTEmployeeHistoryList = function(approve_date) {
        return $http.get('/api/ot/employee/history/?approve_date=' + (approve_date || ''));
    };

    factory.saveOTEmployee = function(data) {
        return $http({
            method: 'post',
            url: '/api/ot/employee/save/',
            data: {params: {'data': data}},
        });
    };

    return factory;
});

app.controller('ctrl', function($scope, $timeout, factory) {
    $scope.ot_open_list = [];
    $scope.ot_history_list = [];
    $scope.decimal_digits = 2;

    $scope.approve_date = '';

    $scope.getOTEmployeeList = function() {
        $scope.myPromise = factory.getOTEmployeeList();
        $scope.myPromise.then(function(res) {
            if (!res.data.ok) {
                alert(res.data.msg);
                return;
            }
            $scope.ot_open_list = res.data.rows;
        });
    };

    $scope.getOTEmployeeHistoryList = function() {
        factory.getOTEmployeeHistoryList().then(function(res) {
            $scope.ot_history_list = res.data.rows;
        });
    };

    $scope.saveOTEmployee = function() {
        factory.saveOTEmployee($scope.ot_open_list).then(function(res) {
            if (res.data.result.ok) {
                alert('Save completed');
                $scope.init();
            }
        });
    };

    $scope.$watch('ot_open_list', function() {
        $scope.ot_total_rate = 0;
        $scope.ot_total_hours = 0;
        $scope.ot_total_amount = 0;
        angular.forEach($scope.ot_open_list, function(item) {
            item.amount = calculateOTAmount(item.salary, item.cfg_workday_per_month, item.cfg_workhour_per_day, item.ot_rate, item.hours);
            $scope.ot_total_rate += item.ot_rate;
            $scope.ot_total_hours += parseFloat(item.hours || '0');
            $scope.ot_total_amount += item.amount;
        });
    }, true);

    $scope.$watch('ot_history_list', function() {
        $scope.ot_history_total_rate = 0;
        $scope.ot_history_total_hours = 0;
        $scope.ot_history_total_amount = 0;
        angular.forEach($scope.ot_history_list, function(item) {
            $scope.ot_history_total_rate += item.ot_rate;
            $scope.ot_history_total_hours += parseFloat(item.hours || '0');
            $scope.ot_history_total_amount += item.amount;
        });
    }, true);

    $scope.filterByApproveDate = function() {
        factory.getOTEmployeeHistoryList($scope.approve_date).then(function(res) {
            $scope.ot_history_list = res.data.rows;
        });
    };

    $scope.init = function() {
        $scope.approve_date = '';
        $scope.getOTEmployeeList();
        $scope.getOTEmployeeHistoryList();
    };

    $scope.init();
});
