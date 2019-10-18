import React from 'react';
import AppBar from '@material-ui/core/AppBar';
import ToolBar from '@material-ui/core/ToolBar';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';
import {
  useStyles,
  theme
} from '../utils/ui-utils'
import { Link } from 'react-router-dom';

class NavBar extends React.Component {
  state = {
    value: 2
  };

  handleChange = (event, value) => {
    this.setState({ value });
  };

  render() {
    return (
        <nav>
          <div class="nav-wrapper">
            <a href="#" class="brand-logo right">יעמוד</a>
            <ul id="nav-mobile" class="left hide-on-med-and-down">
              <li><Link to="/">ניהול בית כנסת</Link></li>
              <li><Link to="/findSynagouge">חיפוש מניין</Link></li>
              <li><Link to="/about">אודות</Link></li>
            </ul>
          </div>
        </nav>
    );
  }
}

export default NavBar;
