import React from 'react';
import { Table, Divider, Tag } from 'antd';
const { Column, ColumnGroup } = Table;

const data = [
  {
    key: '1',
    name: 'John Brown',
    age: 32,
    address: 'New York No. 1 Lake Park',
    tags: ['nice', 'developer'],
  },
  {
    key: '2',
    name: 'Jim Green',
    age: 42,
    address: 'London No. 1 Lake Park',
    tags: ['loser'],
  },
  {
    key: '3',
    name: 'Joe Black',
    age: 32,
    address: 'Sidney No. 1 Lake Park',
    tags: ['cool', 'teacher'],
  },
];

export default class MembersTable extends React.Component {
	render() {
		return (
			<Table dataSource={data}>
				<Column title="*" dataIndex="action"   />
				<Column title="שם פרטי" dataIndex="firstName"   />
				<Column title="שם משפחה" dataIndex="lastName"   />
				<Column title="מין" dataIndex="age"   />
				<Column title="שם אב" dataIndex="address"   />
				<Column title="שם אם" dataIndex="address2"   />
				<Column title="שם עליה לתורה" dataIndex="addres3s"   />
				<Column title="תאריך לידה" dataIndex="addre4ss"   />
				<Column title="יחוס" dataIndex="addre5ss"   />
				<Column title="פרשת בר מצווה" dataIndex="ad5dress"   />
				<Column title="תאריך עלייה אחרונה" dataIndex="6address"   />
				<Column title="שם אישה/בעל" dataIndex="ad4dress"   />
				<Column title="מספר ילדים" dataIndex="addr3ess"   />
			{/* <Column
				title="Tags"
				dataIndex="tags"
				key="tags"
				render={tags => (
					<span>
						{tags.map(tag => (
							<Tag color="blue" key={tag}>
								{tag}
							</Tag>
						))}
					</span>
				)}
			/> */}
		</Table>
		)
	}
}