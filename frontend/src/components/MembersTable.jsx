import React from 'react';
import { Table, TableRow, TableCell, TableHead, TableBody, CircularProgress } from '@material-ui/core'
import MemberRow from './MemberRow';
import { getPersonsInSynagouge } from '../services/api.service';

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
        const { isLoading, data } = this.state;

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