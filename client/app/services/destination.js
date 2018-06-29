function Destination($resource) {
  const actions = {
    get: { method: 'GET', cache: false, isArray: false },
    query: { method: 'GET', cache: false, isArray: true },
  };

  // eslint-disable-next-line no-undef
  const DestinationResource = $resource(`${API_ROOT}/destinations/:id`, { id: '@id' }, actions);

  return DestinationResource;
}

export default function init(ngModule) {
  ngModule.factory('Destination', Destination);
}
