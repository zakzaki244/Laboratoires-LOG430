import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  vus: 50,           // Nombre d'utilisateurs virtuels en même temps
  duration: '60s',   // Pendant 30 secondes
};

export default function () {
  http.get('http://10.194.32.174:5000/');
  sleep(1);  // Attente d’1 seconde entre chaque requête par utilisateur
}
