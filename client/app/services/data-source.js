export const SCHEMA_NOT_SUPPORTED = 1;
export const SCHEMA_LOAD_ERROR = 2;

function DataSource($q, $resource, $http) {
  function fetchSchema(dataSourceId, refresh = false) {
    const params = {};

    if (refresh) {
      params.refresh = true;
    }

    // eslint-disable-next-line no-undef
    return $http.get(`${API_ROOT}/data_sources/${dataSourceId}/schema`, { params });
  }

  const actions = {
    get: { method: 'GET', cache: false, isArray: false },
    query: { method: 'GET', cache: false, isArray: true },
    test: {
      method: 'POST',
      cache: false,
      isArray: false,
      // eslint-disable-next-line no-undef
      url: `${API_ROOT}/data_sources/:id/test`,
    },
  };

    // eslint-disable-next-line no-undef
  const DataSourceResource = $resource(`${API_ROOT}/data_sources/:id`, { id: '@id' }, actions);

  DataSourceResource.prototype.getSchema = function getSchema(refresh = false) {
    if (this._schema === undefined || refresh) {
      return fetchSchema(this.id, refresh).then((response) => {
        const data = response.data;

        this._schema = data;

        return data;
      });
    }

    return $q.resolve(this._schema);
  };

  return DataSourceResource;
}

export default function init(ngModule) {
  ngModule.factory('DataSource', DataSource);
}
