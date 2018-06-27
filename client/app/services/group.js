function Group($resource) {
  const actions = {
    get: { method: 'GET', cache: false, isArray: false },
    query: { method: 'GET', cache: false, isArray: true },
    members: {
      // eslint-disable-next-line no-undef
      method: 'GET', cache: false, isArray: true, url: `${API_ROOT}/groups/:id/members`,
    },
    dataSources: {
      // eslint-disable-next-line no-undef
      method: 'GET', cache: false, isArray: true, url: `${API_ROOT}/groups/:id/data_sources`,
    },
  };
  // eslint-disable-next-line no-undef
  const resource = $resource(`${API_ROOT}/groups/:id`, { id: '@id' }, actions);
  return resource;
}

export default function init(ngModule) {
  ngModule.factory('Group', Group);
}
