import http from 'k6/http';
import { sleep, check } from 'k6';

export let options = {
  vus: 200,
  duration: '60s',
};

const headers = {
  headers: {
    'Authorization': 'Bearer Supermarcher22102002',
    'Content-Type': 'application/json',
  },
};

export default function () {
  const productId = 1; // ID d’un produit existant
  const payload = JSON.stringify({
    name: "Oreo",
    category: "Snack",
    price: 2.5,
    stock: Math.floor(Math.random() * 100),
    store_id: 1,
  });

  const res = http.put(`http://10.194.32.174:5000/api/products/${productId}`, payload, headers);
  check(res, {
    'update status 200': (r) => r.status === 200,
  });
  sleep(1);
}
