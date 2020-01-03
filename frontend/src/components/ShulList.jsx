import React from 'react';
import axios from 'axios';

class ShulList extends React.Component {
state = {
  shuls: [],
  found: false
}

componentDidMount(){
  axios.get("http://192.168.1.20:8000/synagogue")
  .then(response => response.data)
  .then(data => this.setState(
    {shuls: data,
    found: true}
  ));
}

  render() {
    const { shuls, found } = this.state;
    const shulsList = found ? (
      shuls.map(
        shul => {
          return <p>{shul}</p>
        }
      )
    ) : (
      <p>please wait</p>
    );
  return shulsList;
  }
}

export default ShulList;
