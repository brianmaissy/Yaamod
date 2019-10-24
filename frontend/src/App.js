import React from 'react';
import NavBar from './components/NavBar'
import LoginForm from './components/Login'
import Container from '@material-ui/core/Container';

import {
  BrowserRouter as Router,
  Switch,
  Route
} from 'react-router-dom';
import About from './components/About';


class App extends React.Component {
  render() {
    return (
    <Router>
      <NavBar />
      <Switch>
        <Route exact path='/' component={LoginForm} />
        <Route path='/about' component={About} />
      </Switch>
    </Router>
    );
  }
}

export default App;
