import React from 'react';
import { TableCell, TableRow, Link } from '@material-ui/core';

const NullableCell = (props) => <TableCell {...props}>{props.children || '-'}</TableCell>

export default class MemberRow extends React.Component {
	render() {
		const { data } = this.props;
		const { first_name, last_name, gender, father_json, mother_json, paternal_name, date_of_birth, yichus,
				bar_mitzvah_parasha, last_aliya_date, wife_json, num_of_children } = data;

		return (
			<TableRow>
				<NullableCell>{first_name}</NullableCell>
				<NullableCell>{last_name}</NullableCell>
				<NullableCell>{gender}</NullableCell>
				<NullableCell>
					{
						father_json
						&&
						<Link onClick={() => console.log('click on father', father_json.id)}>{father_json.name}</Link	>
					}
				</NullableCell>
				<NullableCell>
					{
						mother_json
						&&
						<Link onClick={() => console.log('click on mother', mother_json.id)}>{mother_json.name}</Link>
					}
				</NullableCell>
				<NullableCell>{paternal_name}</NullableCell>
				<NullableCell>{date_of_birth}</NullableCell>
				<NullableCell>{yichus}</NullableCell>
				<NullableCell>{bar_mitzvah_parasha}</NullableCell>
				<NullableCell>{last_aliya_date}</NullableCell>
				<NullableCell>
					{
						wife_json
						&&
						<Link onClick={() =>console.log('click on wife', wife_json.id)}>{wife_json.name}</Link>
					}
				</NullableCell>
				<NullableCell>{num_of_children}</NullableCell>
			</TableRow>
		);
	}
}