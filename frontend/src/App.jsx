import React from 'react';
import NavBar from './components/NavBar'
import ShulList from './components/ShulList'
import ManageRouter from './components/ManageRouter'
// import About from './components/About';
import he_IL from 'antd/es/locale/he_IL';
import { ConfigProvider } from 'antd';


import {
  BrowserRouter as Router,
  Switch,
  Route,
} from 'react-router-dom';
import MembersTable from './components/MembersTable';

class App extends React.Component {
  constructor(props){
    super(props);

    this.state = {
      token: null
    }
  }
  updateToken(token) {
    this.setState({token: token})
  }
  render() {
    return (
    <ConfigProvider locale={he_IL}>
      <Router>
        <NavBar token={this.state.token} onUpdateToken={this.updateToken.bind(this)}/>
        <Switch>
          <Route path='/manage' component={ManageRouter} />
          <Route path='/findPrayer' component={ShulList} />
          <Route path='/about' component={MembersTable} />
        </Switch>
      </Router>
    </ConfigProvider>
    );
  }
}

export default App;
