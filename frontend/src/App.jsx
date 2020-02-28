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
import RTL from './RTL';
import SynagoguePage from './pages/SynagoguePage';

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
			<RTL>
				<ConfigProvider locale={he_IL} direction='rtl'>
					<Router>
						<NavBar token={this.state.token} onUpdateToken={this.updateToken.bind(this)}/>
						<Switch>
							<Route path='/manage' component={ManageRouter} />
							<Route path='/findPrayer' component={ShulList} />
							<Route path='/about' component={SynagoguePage} />
						</Switch>
					</Router>
				</ConfigProvider>
			</RTL>
    );
  }
}

export default App;
