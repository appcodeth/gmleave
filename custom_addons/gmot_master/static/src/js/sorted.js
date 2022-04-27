angular.module('sorted', []).directive('sorted', function () {
  return {
    scope: true,
    transclude: true,
    template: '<a href="#" ng-click="doSort()" ng-transclude></a><span ng-show="doShow(true)"><i class="fa fa-caret-down"></i></span><span ng-show="doShow(false)"><i class="fa fa-caret-up"></i></span>',
    controller: function ($scope, $element, $attrs) {
      $scope.sorted = $attrs.sorted;
      $scope.doSort = function () {
        $scope.sortBy($scope.sorted);
      };
      $scope.doShow = function (asc) {
        return (asc != $scope.desc) && ($scope.sort == $scope.sorted);
      };
    }
  };
});
