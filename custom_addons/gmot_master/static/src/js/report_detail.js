var app = angular.module('app', ['cgBusy']).config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('@{').endSymbol('}');
});

app.factory('factory', function($http) {
    var factory = {};

    factory.getReportList = function(approve) {
        return $http.get('/api/report/detail/?approve=' + approve);
    };

    factory.getReportDetailEmployeeList = function(id, approve) {
        return $http.get('/api/report/detail/employee/?id=' + id + '&approve=' + approve);
    };

    factory.getReportDetailEmployeeExcel = function(id, approve) {
        return $http.get('/api/report/detail/employee/xlsx/?id=' + id + '&approve=' + approve);
    };

    return factory;
});

function getDate(s) {
    var temps = s.split('/');
    return temps[2] + '-' + temps[1] + '-' + temps[0];
}

app.controller('ctrl', function($scope, $timeout, factory) {
    $scope.report_list = [];
    $scope.decimal_digits = 2;
    $scope.total_ot = 0;
    $scope.total_hours = 0;
    $scope.total_amount = 0;
    $scope.ot = {};
    $scope.ot_employee_list = [];
    $scope.ot_emp_total_hour = 0;
    $scope.ot_emp_total_amount = 0;

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
        $scope.ot = {};
        $scope.getReportList();
    };

    $scope.otByEmployee = function(p) {
        $scope.ot = p;
        factory.getReportDetailEmployeeList(p.id, getDate(p.approve_date)).then(function(res) {
            $scope.ot_employee_list = res.data.rows;
            $('#otReportEmployeeModal').modal('show');
        });
    };

    $scope.otByEmployeeToExcel = function() {
        var p = $scope.ot;
        window.location.href = '/api/report/detail/employee/xlsx?id=' + p.id + '&approve=' + getDate(p.approve_date);
        $('#otReportEmployeeModal').modal('hide');
    };

    $scope.$watch('ot_employee_list', function() {
        $scope.ot_emp_total_hour = 0;
        $scope.ot_emp_total_amount = 0;
        angular.forEach($scope.ot_employee_list, function(item) {
            $scope.ot_emp_total_hour += item.total_hour;
            $scope.ot_emp_total_amount += item.total_amount;
        });
    }, true);

    $scope.init();
});
