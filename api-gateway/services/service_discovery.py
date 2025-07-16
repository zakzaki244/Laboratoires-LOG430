import requests
from flask import current_app

class ServiceDiscovery:
    @staticmethod
    def forward_request(service_url, method, path, headers=None, params=None, json_data=None):
        """Forward une requête vers un microservice"""
        try:
            url = f"{service_url}{path}"
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=10
            )
            
            return response.json(), response.status_code
            
        except requests.RequestException as e:
            return {'message': f"Erreur de communication avec le service: {str(e)}"}, 503
        except Exception as e:
            return {'message': f"Erreur interne: {str(e)}"}, 500

    @staticmethod
    def get_service_url(service_name):
        """Retourne l'URL du service demandé"""
        service_urls = {
            'customer': current_app.config['CUSTOMER_SERVICE_URL'],
            'product': current_app.config['PRODUCT_SERVICE_URL'],
            'sales': current_app.config['SALES_SERVICE_URL'],
            'store': current_app.config['STORE_SERVICE_URL'],
            'cart': current_app.config['CART_SERVICE_URL'],
            'checkout': current_app.config['CHECKOUT_SERVICE_URL']
        }
        return service_urls.get(service_name)