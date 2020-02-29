import React from 'react';
import { Table, TableRow, TableCell, TableHead, TableBody, CircularProgress } from '@material-ui/core'
import MemberRow from './MemberRow';
import _ from 'lodash';
import { getPersonsInSynagouge } from '../services/api.service';

const mockData = [
		{
			id: 1,
			"first_name": "Reuven",
			"last_name": "Levi",
			"gender_name": "Male",
			"paternal_name": "Reuven בן Dad",
			"maternal_name": "Reuven בן Mom",
			"yichus_name": "Levi",
			"father_json": {
					"id": 1,
					"name": "Dad"
			},
			"mother_json": {
					"id": 2,
					"name": "Mom"
			},
			"wife_json": {
					"id": 7,
					"name": "Rivkah Levi"
			},
			"num_of_children": 1
	}
];

const data = _.map(_.range(0, 10), (eln, i) => ({...mockData[0], id: i}));

export default class MembersTable extends React.Component {
	_isMounted;
	constructor(props) {
		super(props);
		this.state = {
			isLoading: true,
			data: {}
		};
	}
	
	componentDidMount() {
		this._isMounted = true;
		this.getData()
	}

	getData = async () => {
		const data = await getPersonsInSynagouge();

		// Make sure compoennt is still mounted
		if (!this._isMounted) return;

		this.setState({
			data,
			isLoading: false
		});
	}

	componentWillUnmount() {
		this._isMounted = false;
	}

	render() {
		const { isLoading } = this.state;

		if (isLoading) {
			return (
				<CircularProgress />
			)
		}

		return (
			<Table>
				<TableHead>
					<TableRow>
						<TableCell>שם פרטי</TableCell>
						<TableCell>שם משפחה</TableCell>
						<TableCell>מין</TableCell>
						<TableCell>שם אב</TableCell>
						<TableCell>שם אם</TableCell>
						<TableCell>שם עליה לתורה</TableCell>
						<TableCell>תאריך לידה</TableCell>
						<TableCell>יחוס</TableCell>
						<TableCell>פרשת בר מצווה</TableCell>
						<TableCell>תאריך עלייה אחרונה</TableCell>
						<TableCell>אישה/בעל</TableCell>
						<TableCell>מספר ילדים</TableCell>
					</TableRow>
				</TableHead>
				<TableBody>
					{
						data.map(row => <MemberRow key={row.id} data={row}></MemberRow>)
					}
				</TableBody>
			</Table>
		);
	}
}