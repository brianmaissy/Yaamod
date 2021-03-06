import React from 'react';
import { Steps, Button, message } from 'antd';
import Register from './Register'

const { Step } = Steps;

const steps = [
  {
    title: 'פרטי התחברות',
    content: Register,
  },
  {
    title: 'פרטי בית הכנסת',
    content: Register,
  },
  {
    title: 'אישור התנאים',
    content: 'Last-content',
  },
  {
    title: 'סיום',
    content: 'Last-content',
  },
];

class RegisterSteps extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      current: 0,
      userDetails: {}
    };
  }

  next() {
    const current = this.state.current + 1;
    this.setState({ current });
  }

  prev() {
    const current = this.state.current - 1;
    this.setState({ current });
  }

  render() {
    const { current } = this.state;
    const CurrentSteps = steps[current].content
    return (
      <div>
        <Steps current={current}>
          {steps.map(item => (
            <Step key={item.title} title={item.title} />
          ))}
        </Steps>
        <div className="steps-content">
            <CurrentSteps config={this.state} onUpdateConfig={this.updateConfig}    />
        </div>
        <div className="steps-action">
          {current < steps.length - 1 && (
            <Button type="primary" onClick={() => this.next()}>
              Next
            </Button>
          )}
          {current === steps.length - 1 && (
            <Button type="primary" onClick={() => message.success('Processing complete!')}>
              Done
            </Button>
          )}
          {current > 0 && (
            <Button style={{ marginLeft: 8 }} onClick={() => this.prev()}>
              Previous
            </Button>
          )}
        </div>
      </div>
    );
  }
}

export default RegisterSteps;
