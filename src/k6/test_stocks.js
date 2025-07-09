import http from 'k6/http';
import { sleep, check } from 'k6';

export let options = {
  stages: [
    { duration: '10s', target: 20 },
    { duration: '30s', target: 20 },
    { duration: '10s', target: 0 },
  ],
};

const headers = {
  headers: {
    Authorization: 'Bearer Supermarcher22102002',
  },
};

export default function () {
  const ids = [1, 2, 3]; // Ids de magasins à tester
  for (const id of ids) {
    const res = http.get(`http://10.194.32.174:5000/api/magasins/${id}`, headers);
    check(res, {
      'status 200': (r) => r.status === 200,
    });
    sleep(0.5);
  }
}
