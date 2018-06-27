function AlertSubscription($resource) {
  // eslint-disable-next-line no-undef
  const resource = $resource(`${API_ROOT}/alerts/:alertId/subscriptions/:subscriberId`, { alertId: '@alert_id', subscriberId: '@id' });
  return resource;
}

export default function init(ngModule) {
  ngModule.factory('AlertSubscription', AlertSubscription);
}
