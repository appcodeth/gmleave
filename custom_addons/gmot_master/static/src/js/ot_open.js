var app = angular.module('app', ['cgBusy', 'bw.paging', 'sorted']).config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('@{').endSymbol('}');
});

app.factory('factory', function($http) {
    var factory = {};

    factory.getOTList = function(page, rp, sort, desc) {
        return $http.get('/api/ot/list/?page=' + page + '&rp=' + rp + '&sort=' + sort + '&desc=' + desc);
    };

    factory.saveOT = function(data) {
        return $http({
            method: 'post',
            url: '/api/ot/save/',
            data: {params: {'data': data}},
        });
    };

    factory.getOT = function(id) {
        return $http.get('/api/ot/get/?id=' + id);
    };

    factory.deleteOT = function(id) {
        return $http.get('/api/ot/delete/?id=' + id);
    };

    return factory;
});

function isValidDate(date) {
    var temp = date.split('/');
    var d = new Date(temp[1] + '/' + temp[0] + '/' + temp[2]);
    return (d && (d.getMonth() + 1) == temp[1] && d.getDate() == Number(temp[0]) && d.getFullYear() == Number(temp[2]));
}

app.controller('ctrl', function($scope, $timeout, factory) {
    $scope.ot_list = [];
    $scope.page = 1;
    $scope.rp = 20;
    $scope.decimal_digits = 2;

    $scope.sortBy = function (ord) {
        $scope.desc = ($scope.sort === ord) ? !$scope.desc : true;
        $scope.sort = ord;
        $scope.getOTList();
    };

    $scope.getOTList = function() {
        $scope.myPromise = factory.getOTList($scope.page, $scope.rp, $scope.sort, $scope.desc);
        $scope.myPromise.then(function(res) {
            $scope.ot_list = res.data.rows;
            $scope.total = res.data.total;
            $scope.pageCount = res.data.page_count;
            $scope.totalPages = res.data.total_pages;
        });
    };

    $scope.clearOTModal = function() {
        $('#ot_id').val('');
        $('#ot_date').val('');
        $('#ot_rate').val('');
        $('#ot_employee').val('');
        $('#otModal .ms-options-wrap button').html('- เลือก -');
        $('#otModal input[type=checkbox]').prop('checked', false);
        $('#otModal ul li').removeClass('selected');
        $('.datepicker').datepicker("update", new Date());
    };

    $scope.saveOT = function() {
        if ($('#ot_date').val() && $('#ot_rate').val() && $('#ot_employee').val().length) {} else {
            Swal.fire({
                icon: 'error',
                title: 'ข้อมูลไม่ถูกต้อง',
                text: 'กรุณากรอกข้อมูลให้ครบถ้วน',
            });
            return;
        }

        var err = '';
        var result = isValidDate($('#ot_date').val());
        if(!result) {
            err = 'กรุณากรอกวันที่ OT ให้ถูกต้อง!\n';
        }

        result = !/^\s*$/.test($('#ot_rate').val()) && !isNaN($('#ot_rate').val());
        if(!result) {
            err = 'กรุณากรอกอัตราจ่าย (Rate) ให้ถูกต้อง!\n';
        }

        if(err) {
            Swal.fire({
                icon: 'error',
                title: 'ข้อมูลไม่ถูกต้อง',
                text: err,
            });
            return;
        }

        data = {
            'id': $('#ot_id').val(),
            'date': $('#ot_date').val(),
            'rate': $('#ot_rate').val(),
            'employees': $('#ot_employee').val(),
        }
        factory.saveOT(data).then(function(res) {
            if (res.data.result.ok) {
                $('#otModal').modal('hide');
                Swal.fire({
                  position: 'top-center',
                  icon: 'success',
                  title: 'บันทึกข้อมูลแล้ว',
                  showConfirmButton: false,
                  timer: 1500
                });
                $scope.init();
            }
        });
    };

    $scope.addOTModal = function() {
        $scope.clearOTModal();
        $('#otModal').modal('show');
    };

    $scope.editOT = function(id) {
        $scope.clearOTModal();
        factory.getOT(id).then(function(res) {
            var ot = res.data.rows;
            $('.datepicker').datepicker('update', new Date(ot.date));
            $('#ot_id').val(ot.id);
            $('#ot_rate').val(ot.rate);
            $('#otModal input[type=checkbox]').each(function() {
                if (ot.employees.includes(parseInt(this.value, 10))) {
                    this.click();
                }
            });
            $('#otModal').modal('show');
        });
    };

    $scope.deleteOT = function(id) {
        $.confirm({
            title: 'ยืนยัน',
            content: 'คุณต้องการลบข้อมูล OT ใช่หรือไม่ ?',
            buttons: {
                confirm: {
                    btnClass: 'btn-danger',
                    text: 'ยืนยัน',
                    action: function () {
                        $scope.doDelete(id);
                    },
                },
                cancel: {
                    text: 'ยกเลิก',
                },
            }
        });
    };

    $scope.doDelete = function(id) {
        factory.deleteOT(id).then(function(res) {
            if (!res.data.ok) {
                Swal.fire({
                    icon: 'error',
                    title: 'เกิดความผิดพลาด',
                    text: res.data.msg,
                });
                return;
            }
            Swal.fire({
              position: 'top-center',
              icon: 'success',
              title: 'ลบข้อมูลเรียบร้อยแล้ว',
              showConfirmButton: false,
              timer: 1500
            });
            $scope.getOTList();
        });
    };

    $scope.setPage = function (e, page) {
        $scope.page = page;
        if (page) {
            $scope.getOTList();
        }
    };

    $scope.init = function() {
        $scope.sort = 'date';
        $scope.desc = true;
        $scope.search = {};
        $scope.page = 1;
        $scope.getOTList();
    };

    $scope.init();
});

$(function() {
    $('.datepicker').datepicker({
        clearBtn: true,
        format: 'dd/mm/yyyy',
    }).datepicker('update', new Date());

    $.get('/api/employee/list', function(data, status) {
        $.each(data.rows, function(i, item) {
            $('#ot_employee').append($('<option>', {
                value: item.id,
                text: item.name,
            }));
        });

        $('#ot_employee').multiselect({
            columns: 1,
            placeholder: '- เลือก -',
            search: false,
            selectAll: true,
        });
    });
});
