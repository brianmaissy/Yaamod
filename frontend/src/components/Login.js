import React from 'react';
import 'antd/dist/antd.css';
import { Link } from 'react-router-dom';

import { Form, Icon, Input, Button, Checkbox, Layout, Card} from 'antd';
import './Login.css'

const { Content } = Layout;

class NormalLoginForm extends React.Component {
  handleSubmit = e => {
    const { onUpdateToken } = this.props;
    e.preventDefault();
    this.props.form.validateFields((err, values) => {
      if (!err) {
        console.log('Received values of form: ', values);
      }
    });
    fetch("api-auth").then(response => {
      onUpdateToken(response.newToken)
    })

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
                type='email'
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

            <a className="login-form-forgot" href="">
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
