function OrganizationStatus($http) {
  this.objectCounters = {};

  this.refresh = () =>
  // eslint-disable-next-line no-undef
    $http.get(`${API_ROOT}/organization/status`).then(({ data }) => {
      this.objectCounters = data.object_counters;
      return this;
    });
}

export default function init(ngModule) {
  ngModule.service('OrganizationStatus', OrganizationStatus);
}
