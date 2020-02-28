import React from 'react';
import MembersTable from '../components/MembersTable';
import { withStyles } from '@material-ui/core'

class SynagoguePage extends React.Component {
	render() {
		const { classes } = this.props;
		return (
			<div className={classes.container}>
				{/*
					 synagoue will be recived later and used to get members (on members container) 
				   for now we use mock data only.
				*/}
				<MembersTable synagogueId={1}></MembersTable>
			</div>
		)
	}
}

const styles = (theme) => ({
	container: {
		padding: theme.spacing(4)
	}
});

export default withStyles(styles)(SynagoguePage);