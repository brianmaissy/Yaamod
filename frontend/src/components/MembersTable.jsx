import React from 'react';
import { Table, TableRow, TableCell, TableHead, TableBody } from '@material-ui/core'
import MemberRow from './MemberRow';

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
	render() {
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