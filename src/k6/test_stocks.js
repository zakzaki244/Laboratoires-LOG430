import http from 'k6/http';
import { sleep, check } from 'k6';

export let options = {
  stages: [
    { duration: '10s', target: 200 },
    { duration: '60s', target: 200 },
    { duration: '10s', target: 200 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

const headers = {
  headers: {
    Authorization: 'Bearer Supermarcher22102002',
  },
};

export default function () {
  const ids = [1, 2, 3];
  for (const id of ids) {
    const res = http.get(`http://10.194.32.174:5000/api/magasins/${id}`, headers);
    check(res, {
      'status 200': (r) => r.status === 200,
    });
    sleep(0.5);
  }
}
