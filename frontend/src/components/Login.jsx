import React from 'react';
import 'antd/dist/antd.css';
import { Link } from 'react-router-dom';
import axios from 'axios';


import { Form, Icon, Input, Button, Card} from 'antd';
import './Login.css'

// const { Content } = Layout;

class NormalLoginForm extends React.Component {
  handleSubmit = e => {
    e.preventDefault();
    this.props.form.validateFields((err, values) => {
      if (!err) {
        console.log('Received values of form: ', values);
        // TODO: fix CORS thing
        axios.post("http://192.168.1.20:8000/login", {
          username: values.username,
          password: values.password
        }
      ).then(response => {
        console.log(response)
      }
          // onUpdateToken(response.newToken)
      )}}
    )
  };

  render() {
    const { getFieldDecorator } = this.props.form;
    return (
     <Card style={{ padding: '25px 25%' }}>
        <Form onSubmit={this.handleSubmit} className="login-form" labelCol='span'>
          <Form.Item>
            {getFieldDecorator('username', {
              rules: [{ required: true, message: 'Please input your username!' }],
            })(
              <Input
                prefix={<Icon type="user" style={{ color: 'rgba(0,0,0,.25)' }} />}
                type='text'
                placeholder="Username"
              />,
            )}
          </Form.Item>
          <Form.Item>
            {getFieldDecorator('password', {
              rules: [{ required: true, message: 'Please input your Password!' }],
            })(
              <Input
                prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />}
                type="password"
                placeholder="Password"
              />,
            )}
          </Form.Item>
          <Form.Item>

						{/* #0 is for empty link */}
            <a className="login-form-forgot" href="#0">
              Forgot password?
            </a>
            <Button type="primary" htmlType="submit" className="login-form-button" icon="login">
              Log in
            </Button>
             Or <Link to="/manage/register">register now!</Link>
          </Form.Item>
        </Form>
      </Card>
    );
  }
}


const LoginForm = Form.create({ name: 'normal_login' })(NormalLoginForm);
export default LoginForm;
