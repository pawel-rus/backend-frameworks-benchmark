import http from 'k6/http';
import { check } from 'k6';

export let options = {
    vus: 100,
    duration: '30s',
};

const PORT = __ENV.PORT || '3001';
const ERROR_RATE = parseFloat(__ENV.ERROR_RATE || '0.0');

export default function () {
    const url = `http://localhost:${PORT}/exceptions`;
    
    const isError = Math.random() < ERROR_RATE;
    
    let headers = {};
    
    if (!isError) {
        headers['Authorization'] = 'Bearer secret-token';
    }

    let res = http.post(url, null, { headers: headers });

    check(res, {
        'status is correct (200 or 401)': (r) => isError ? r.status === 401 : r.status === 200,
    });
}