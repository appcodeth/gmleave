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


app.controller('ctrl', function($scope, $timeout, factory) {
    $scope.ot_list = [];
    $scope.page = 1;
    $scope.rp = 5;

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
        $('#otModal .ms-options-wrap button').html('- Select -');
        $('#otModal input[type=checkbox]').prop('checked', false);
        $('#otModal ul li').removeClass('selected');
        $('.datepicker').datepicker("update", new Date());
    };

    $scope.saveOT = function() {
        if ($('#ot_date').val() && $('#ot_rate').val() && $('#ot_employee').val().length) {} else {
            alert('Please enter all OT data!');
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
                  title: 'Save completed',
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
        if (!confirm('Confirm delete OT?')) {
            return;
        }

        factory.deleteOT(id).then(function(res) {
            if (!res.data.ok) {
                Swal.fire({
                    icon: 'error',
                    title: 'Alert',
                    text: res.data.msg,
                });
                return;
            }
            Swal.fire({
              position: 'top-center',
              icon: 'success',
              title: 'Delete success',
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
            placeholder: '- Select -',
            search: false,
            selectAll: true,
        });
    });
});
