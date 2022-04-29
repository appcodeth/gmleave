var app = angular.module('app', ['cgBusy']).config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('@{').endSymbol('}');
});

app.factory('factory', function($http) {
    var factory = {};

    factory.getOTApproveDraftList = function(id) {
        return $http.get('/api/ot/approve/draft/list/?emp_id=' + id);
    };

    factory.doApproveOT = function(id) {
        return $http.get('/api/ot/approve/confirm/?emp_id=' + id);
    };

    return factory;
});

app.controller('ctrl', function($scope, $timeout, factory) {
    $scope.ot_open_list = [];
    $scope.decimal_digits = 2;

    $scope.getOTApproveDraftList = function(id) {
        $scope.myPromise = factory.getOTApproveDraftList(id);
        $scope.myPromise.then(function(res) {
            if (!res.data.ok) {
                Swal.fire({
                    icon: 'error',
                    title: 'เกิดความผิดพลาด',
                    text: res.data.msg,
                });
                return;
            }
            $scope.ot_open_list = res.data.rows;
        });
    };

    $scope.$watch('ot_open_list', function() {
        $scope.ot_total_rate = 0;
        $scope.ot_total_hours = 0;
        $scope.ot_total_amount = 0;
        angular.forEach($scope.ot_open_list, function(item) {
            $scope.ot_total_rate += item.ot_rate;
            $scope.ot_total_hours += parseFloat(item.hours || '0');
            $scope.ot_total_amount += item.amount;
        });
    }, true);

    $scope.doApproveOT = function() {
        $.confirm({
            title: 'ยืนยัน',
            content: 'คุณต้องการอนุมัติ OT ใช่หรือไม่ ?',
            buttons: {
                confirm: {
                    btnClass: 'btn-primary',
                    text: 'ยืนยัน',
                    action: function () {
                        $scope.actionToApproveOT();
                    },
                },
                cancel: {
                    text: 'ยกเลิก',
                },
            }
        });
    };

    $scope.actionToApproveOT = function() {
        var id = $('#emp_id').val();
        factory.doApproveOT(id).then(function(res) {
            if (res.data.ok) {
                Swal.fire({
                  position: 'top-center',
                  icon: 'success',
                  title: 'อนุมัติเรียบร้อยแล้ว',
                  showConfirmButton: false,
                  timer: 1500
                }).then(() => {
                    window.location.href = '/gmot/ot/approve/history/?id=' + id;
                });
            }
        });
    };

    $scope.init = function() {
        $scope.getOTApproveDraftList($('#emp_id').val());
    };

    $scope.init();
});
