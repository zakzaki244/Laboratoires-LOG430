import http from 'k6/http';
import { sleep, check } from 'k6';

export let options = {
  stages: [
    { duration: '10s', target: 200 },
    { duration: '60s', target: 200 },
    { duration: '10s', target: 50 },
  ],
};

const headers = {
  headers: {
    Authorization: 'Bearer Supermarcher22102002',
  },
};

export default function () {
  const res = http.get('http://10.194.32.174:5000/api/rapport', headers);
  check(res, {
    'status 200': (r) => r.status === 200,
    'rapport contient données': (r) => r.body.includes('stocks'),
  });
  sleep(1);
}
