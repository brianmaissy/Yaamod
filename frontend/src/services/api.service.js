import { PERSON_URL } from '../consts/server_routes';
import Axios from 'axios';

const defaultOnError = (err) => {
    console.error('err ? ', err);
}

const METHODS = {
    GET: 'GET',
    PATCH: 'PATCH',
    DELETE: 'DELETE',
    POST: 'POST'
}

const apiCall = async (url, method=METHODS.GET, data=undefined) => {
    try {
        const axiosRes = await Axios({
            method,
            url,
            data,
            withCredentials: true
        });
        return axiosRes.data;
    } catch(e) {
        defaultOnError(e);
    }
}

export const getPersonsInSynagouge = async () => await apiCall(PERSON_URL);