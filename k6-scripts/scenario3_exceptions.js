import http from 'k6/http';
import { check } from 'k6';

// Configuration of the test: 100 virtual users (VU) for 30 seconds
export let options = {
    vus: 100,
    duration: '30s',
};

// Download configuration from environment variables, with defaults
const PORT = __ENV.PORT || '3001';
const ERROR_RATE = parseFloat(__ENV.ERROR_RATE || '0.0');

// Preparing a JSON payload to send in POST requests
const payload = JSON.stringify([
    { id: 1, name: "ItemA" },
    { id: 2, name: "ItemB" },
    { id: 3, name: "ItemC" }
]);

export default function () {
    const url = `http://localhost:${PORT}/json`;
    
    // Deciding randomly if this request should be a "normal" one or an "error" one based on ERROR_RATE
    const isError = Math.random() < ERROR_RATE;
    
    let headers = { 
        'Content-Type': 'application/json' 
    };
    
    // Key moment: if this is NOT an error, we provide a valid token.
    // If isError == true, we intentionally skip the token, forcing the server to return a 401 error.
    if (!isError) {
        headers['Authorization'] = 'Bearer secret-token';
    }

    // Sending the POST request to the server with the prepared payload and headers
    let res = http.post(url, payload, { headers: headers });

    // Checking the response: if it's a "normal" request, we expect a 200 status. If it's an "error" request, we expect a 401 status.
    check(res, {
        'status 200': (r) => !isError && r.status === 200,
        'status 401': (r) => isError && r.status === 401,
    });
}