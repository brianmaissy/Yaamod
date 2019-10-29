import React from 'react';
import NavBar from './components/NavBar'
import ManageRouter from './components/ManageRouter'
import About from './components/About';


import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect,
} from 'react-router-dom';


class App extends React.Component {

  render() {
    return (
    <Router>
      <NavBar />
      <Switch>
        <Route path='/manage' component={ManageRouter} />
        <Route path='/about' component={About} />
      </Switch>
    </Router>
    );
  }
}

export default App;
