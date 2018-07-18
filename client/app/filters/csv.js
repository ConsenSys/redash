export default function init(ngModule) {
  ngModule.filter('csv', () =>
    function split(value, index) {
      if (!value) {
        return null;
      }

      const parsed = value.split(',').map(v => v.trim());

      if (index >= parsed.length) {
        return null;
      }

      return parsed[index];
    });
}
