function QuerySnippet($resource) {
  // eslint-disable-next-line no-undef
  const resource = $resource(`${API_ROOT}/query_snippets/:id`, { id: '@id' });
  resource.prototype.getSnippet = function getSnippet() {
    let name = this.trigger;
    if (this.description !== '') {
      name = `${this.trigger}: ${this.description}`;
    }

    return {
      name,
      content: this.snippet,
      tabTrigger: this.trigger,
    };
  };

  return resource;
}

export default function init(ngModule) {
  ngModule.factory('QuerySnippet', QuerySnippet);
}
