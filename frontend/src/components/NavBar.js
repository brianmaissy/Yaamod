import React from 'react';
import { Menu, Icon } from 'antd';
import { Link } from 'react-router-dom';
import 'antd/dist/antd.css';


const { SubMenu } = Menu;

class NavBar extends React.Component {
  constructor(props){
    super(props);
  }

  urlToIndex = {
    "": "manage",
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
    return (
      <Menu onClick={this.handleClick} selectedKeys={[this.state.current]} mode="horizontal">
        <Menu.Item key={this.urlToIndex[""]}>
          <Link to="/">
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

export default NavBar;
