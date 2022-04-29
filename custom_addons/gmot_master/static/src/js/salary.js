var app = angular.module('app', ['cgBusy']).config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('@{').endSymbol('}');
});

app.directive('datepicker', function() {
    return {
        restrict: 'A',
        require: 'ngModel',
        compile: function() {
            return {
                pre: function(scope, element, attrs, ngModelCtrl) {
                    var format, dateObj;
                    format = (!attrs.dpFormat) ? 'dd/mm/yyyy' : attrs.dpFormat;
                    if (!attrs.initDate && !attrs.dpFormat) {
                        dateObj = new Date();
                        scope[attrs.ngModel] = dateObj.getDate() + '/' + (dateObj.getMonth() + 1) + '/' + dateObj.getFullYear();
                    } else if (!attrs.initDate) {
                        scope[attrs.ngModel] = attrs.initDate;
                    } else {}

                    // init & set value datepicker
                    $(element).datepicker({
                        format: format,
                        clearBtn: true,
                    }).on('changeDate', function(ev) {
                        scope.$apply(function() {
                            ngModelCtrl.$setViewValue(ev.format(format));
                        });
                    }).datepicker("update", scope['p'].effective_date);

                    // toggle button
                    element.parent().find('.input-group-append').on('click', function() {
                        $(element).datepicker('show');
                    });
                }
            }
        }
    }
});

app.factory('factory', function($http) {
    var factory = {};

    factory.getEmployeeList = function() {
        return $http.get('/api/employee/list/');
    };

    factory.saveEmployee = function(data) {
        params = {'data': data};
        return $http({
            method: 'post',
            url: '/api/employee/save/',
            data: {'params': params},
        });
    };

    factory.getEmployeeHistory = function(id) {
        return $http.get('/api/employee/history/?id=' + id);
    };

    factory.deleteEmployeeHistory = function(history_id, emp_id) {
        return $http.get('/api/employee/history/delete/?id=' + history_id + '&emp_id=' + emp_id);
    };

    return factory;
});

function isValidDate(date) {
    var temp = date.split('/');
    var d = new Date(temp[1] + '/' + temp[0] + '/' + temp[2]);
    return (d && (d.getMonth() + 1) == temp[1] && d.getDate() == Number(temp[0]) && d.getFullYear() == Number(temp[2]));
}

app.controller('ctrl', function($scope, $timeout, factory) {
    $scope.employee_list = [];
    $scope.employee_history_list = [];
    $scope.employee;
    $scope.decimal_digits = 2;

    $scope.getEmployeeList = function() {
        $scope.myPromise = factory.getEmployeeList();
        $scope.myPromise.then(function(res) {
            $scope.employee_list = res.data.rows;
        });
    };

    $scope.saveEmployee = function() {
        // validate before save
        var err = '';
        angular.forEach($scope.employee_list, function(item) {
            if(item.effective_date && !err) {
                var result = isValidDate(item.effective_date);
                if(!result) {
                    err = 'กรุณากรอกวันที่ให้ถูกต้อง!\n';
                }

                result = !/^\s*$/.test(item.salary) && !isNaN(item.salary);
                if(!result) {
                    err = 'กรุณากรอกเงินเดือนให้ถูกต้อง!\n';
                }
            }
        });

        if(err) {
            Swal.fire({
                icon: 'error',
                title: 'ข้อมูลไม่ถูกต้อง',
                text: err,
            });
            return;
        }

        factory.saveEmployee($scope.employee_list).then(function(res) {
            if (res.data.result.ok) {
                Swal.fire({
                  position: 'top-center',
                  icon: 'success',
                  title: 'บันทึกข้อมูลแล้ว',
                  showConfirmButton: false,
                  timer: 1500
                });
                $scope.getEmployeeList();
            }
        });
    };

    $scope.openHistoryModal = function(employee) {
        $scope.employee = employee;
        factory.getEmployeeHistory(employee.id).then(function(res) {
            $scope.employee_history_list = res.data.rows;
            $('#employeeHistoryModal').modal('show');
        });
    };

    $scope.deleteEmployeeHistory = function(history_id) {
            $.confirm({
            title: 'ยืนยัน',
            content: 'คุณต้องการลบข้อมูล ใช่หรือไม่ ?',
            buttons: {
                confirm: {
                    btnClass: 'btn-danger',
                    text: 'ยืนยัน',
                    action: function () {
                        $scope.doDelete(history_id);
                    },
                },
                cancel: {
                    text: 'ยกเลิก',
                },
            }
        });
    };

    $scope.doDelete = function(history_id) {
        factory.deleteEmployeeHistory(history_id, $scope.employee.id).then(function(res) {
            factory.getEmployeeHistory($scope.employee.id).then(function(hist) {
                $scope.employee_history_list = hist.data.rows;
            });
            $scope.getEmployeeList();
        });
    };

    $scope.init = function() {
        $scope.getEmployeeList();
    };

    $scope.init();
});
