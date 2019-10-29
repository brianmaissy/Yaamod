import React from 'react';
import LoginForm from "./Login"
import Register from "./Register"
import About from "./About"

import {
  Switch,
  Route
} from 'react-router-dom';


class ManageRouter extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      isLoggedIn: false
    };
  }

  render() {
    if (!this.state.isLoggedIn && window.location.pathname === "/manage") {
      this.props.history.push("/manage/login")
    }
    return (
      <Switch>
        <Route exact path='/manage' component={About} />
        <Route exact path='/manage/login' component={LoginForm} />
        <Route exact path='/manage/register' component={Register} />
      </Switch>
    );
  }
}

export default ManageRouter;
