import http from 'k6/http';
import { check } from 'k6';
import { generatePayload } from './payload-generator.js';

export const options = {
    scenarios: {
        constant_request_rate: {
            executor: 'constant-arrival-rate',
            rate: 500,
            timeUnit: '1s',
            duration: '30s',
            preAllocatedVUs: 100,
            maxVUs: 500,
        },
    },

    thresholds: {
        http_req_failed: ['rate<0.01'],
    },
};

const BASE_URL = __ENV.BASE_URL;
const PAYLOAD_KB = parseInt(__ENV.PAYLOAD_KB || '1');

const payload = generatePayload(PAYLOAD_KB);

export default function () {

    const response = http.post(
        `${BASE_URL}/json`,
        payload,
        {
            headers: {
                'Content-Type': 'application/json',
            },
        }
    );

    check(response, {
        'status is 200': (r) => r.status === 200,
    });
}