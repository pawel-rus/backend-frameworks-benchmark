import http from 'k6/http';
import { check } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metric to track connection timeout rate
export let timeoutRate = new Rate('timeout_rate');

// Download configuration from environment variables, with defaults
const PORT = __ENV.PORT || '3001';
const VUS = __ENV.VUS ? parseInt(__ENV.VUS) : 10;
const DURATION = __ENV.DURATION || '60s';

// Configuration of the test: dynamically scaling VUs
export let options = {
    vus: VUS,
    duration: DURATION,
    discardResponseBodies: true, // Optimize RAM by ignoring body contents under high VUs
    // Add 95th and 99th percentiles to the summary output
    summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
};

export default function () {
    // The baseline endpoint for measuring raw concurrency and tail latency
    const url = `http://localhost:${PORT}/io`;

    // Send a GET request. We set a timeout threshold to properly track timeouts under load.
    // 10 seconds is configured to capture untruncated tail latencies under extreme overload while protecting sockets.
    let res = http.get(url, { timeout: '10s' });

    // Check if the response is successful
    check(res, {
        'status 200': (r) => r.status === 200,
    });

    // Track timeouts using k6's error_code (1050 is Request Timeout)
    const isTimeout = res.error_code === 1050 || (res.error && res.error.toLowerCase().includes('timeout'));
    timeoutRate.add(isTimeout ? 1 : 0);
}
