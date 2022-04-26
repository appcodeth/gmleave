var app = angular.module('app', ['cgBusy']).config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('@{').endSymbol('}');
});

app.factory('factory', function($http) {
    var factory = {};

    factory.getOTApproveList = function() {
        return $http.get('/api/ot/approve/list/');
    };

    return factory;
});

app.controller('ctrl', function($scope, $timeout, factory) {
    $scope.ot_approve_list = [];
    $scope.decimal_digits = 2;

    $scope.getOTApproveList = function() {
        $scope.myPromise = factory.getOTApproveList();
        $scope.myPromise.then(function(res) {
            $scope.ot_approve_list = res.data.rows;
        });
    };

    $scope.viewDetail = function(p) {
        window.location.href = '/gmot/ot/approve/draft/?id=' + p.id;
    };

    $scope.viewHistory = function(p) {
        window.location.href = '/gmot/ot/approve/history/?id=' + p.id;
    };

    $scope.init = function() {
        $scope.getOTApproveList();
    };

    $scope.init();
});
