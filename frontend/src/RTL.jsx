import React from 'react';
import { create } from 'jss';
import rtl from 'jss-rtl';
import { StylesProvider, jssPreset, createMuiTheme, ThemeProvider } from '@material-ui/core/styles';

// Configure JSS
const jss = create({ plugins: [...jssPreset().plugins, rtl()] });

const rtlTheme = createMuiTheme({
	direction: 'rtl',
});

export default function RTL(props) {
  return (
    <StylesProvider jss={jss}>
			<ThemeProvider theme={rtlTheme}>
      	{props.children}
			</ThemeProvider>
    </StylesProvider>
  );
}