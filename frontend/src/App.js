import React from 'react';
import NavBar from './components/NavBar'
import ManageRouter from './components/ManageRouter'
import About from './components/About';
import he_IL from 'antd/es/locale/he_IL';
import { ConfigProvider } from 'antd';


import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect,
} from 'react-router-dom';


class App extends React.Component {

  render() {
    return (
      <ConfigProvider locale={he_IL}>  
    <Router>
      <NavBar />
      <Switch>
        <Route path='/manage' component={ManageRouter} />
        <Route path='/about' component={About} />
      </Switch>
    </Router>
    </ConfigProvider>
    );
  }
}

export default App;
