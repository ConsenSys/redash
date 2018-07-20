import React from 'react';
import { react2angular } from 'react2angular';

class Footer extends React.Component {
  render() {
    return null;
  }
}

export default function init(ngModule) {
  ngModule.component('footer', react2angular(Footer, [], ['clientConfig', 'currentUser']));
}
