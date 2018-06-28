function cancelQueryButton() {
  return {
    restrict: 'E',
    scope: {
      queryId: '=',
      taskId: '=',
    },
    transclude: true,
    template: '<button class="btn btn-default" ng-disabled="inProgress" ng-click="cancelExecution()"><i class="zmdi zmdi-spinner zmdi-hc-spin" ng-if="inProgress"></i> Cancel</button>',
    replace: true,
    controller($scope, $http, currentUser, Events) {
      $scope.inProgress = false;

      $scope.cancelExecution = () => {
        // eslint-disable-next-line no-undef
        $http.delete(`${API_ROOT}/jobs/${$scope.taskId}`).success(() => {});

        let queryId = $scope.queryId;
        if ($scope.queryId === 'adhoc') {
          queryId = null;
        }

        Events.record('cancel_execute', 'query', queryId, { admin: true });
        $scope.inProgress = true;
      };
    },
  };
}

export default function init(ngModule) {
  ngModule.directive('cancelQueryButton', cancelQueryButton);
}
