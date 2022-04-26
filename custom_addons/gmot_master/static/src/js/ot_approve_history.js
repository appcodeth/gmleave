var app = angular.module('app', ['cgBusy']).config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('@{').endSymbol('}');
});

app.factory('factory', function($http) {
    var factory = {};

    factory.getOTApproveHistoryList = function(emp_id, approve_date) {
        return $http.get('/api/ot/approve/history/list/?emp_id=' + emp_id + '&approve_date=' + (approve_date || ''));
    };

    return factory;
});

app.controller('ctrl', function($scope, $timeout, factory) {
    $scope.ot_history_list = [];
    $scope.decimal_digits = 2;
    $scope.approve_date = '';

    $scope.getOTApproveHistoryList = function(emp_id, approve_date) {
        $scope.myPromise = factory.getOTApproveHistoryList(emp_id, approve_date);
        $scope.myPromise.then(function(res) {
            $scope.ot_history_list = res.data.rows;
        });
    };

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
        factory.getOTApproveHistoryList($('#emp_id').val(), $scope.approve_date).then(function(res) {
            $scope.ot_history_list = res.data.rows;
        });
    };

    $scope.init = function() {
        $scope.approve_date = '';
        $scope.getOTApproveHistoryList($('#emp_id').val(), '');
    };

    $scope.init();
});
