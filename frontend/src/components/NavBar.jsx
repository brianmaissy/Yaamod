import React from 'react';
import { Menu, Icon } from 'antd';
import { Link, withRouter } from 'react-router-dom';
import 'antd/dist/antd.css';


class NavBar extends React.Component {

  urlToIndex = {
    "manage": "manage",
    "findPrayer": "find",
    "about": "about",
  };

  state = {
    current: this.urlToIndex[window.location.pathname.split("/")[1]]
  };



  handleClick = e => {
    console.log('click ', e);
    this.setState({
      current: e.key,
    });
  };

  render() {
    if (window.location.pathname === "/") {
      this.props.history.push("/manage")
      this.setState({
        current: "manage",
      });
    }
    return (
      <Menu onClick={this.handleClick} selectedKeys={[this.state.current]} mode="horizontal">
        <Menu.Item key={this.urlToIndex["manage"]}>
          <Link to="/manage">
            <Icon type="team" />
            נהל בית כנסת
          </Link>
        </Menu.Item>
        <Menu.Item key={this.urlToIndex["findPrayer"]}>
          <Link to="/findPrayer">
            <Icon type="search" />
            מצא מניין
          </Link>
        </Menu.Item>
        <Menu.Item key={this.urlToIndex["about"]}>
          <Link to="/about">
            <Icon type="info-circle" />
            אודות
          </Link>
        </Menu.Item>
      </Menu>
    );
  }
}

export default withRouter(NavBar);
