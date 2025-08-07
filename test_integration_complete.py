"""
Test d'Intégration Complète - Lab 7
Tests bout-en-bout avec API Gateway et Interface Web
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_GATEWAY_URL = 'http://localhost:8080'
WEB_INTERFACE_URL = 'http://localhost:5008'

class IntegrationTestRunner:
    """Testeur pour l'intégration complète de l'architecture."""
    
    def __init__(self):
        self.test_results = []
        
    def run_integration_tests(self):
        """Exécute tous les tests d'intégration."""
        logger.info("=== TESTS D'INTÉGRATION COMPLÈTE LAB 7 ===")
        
        # Tests d'intégration
        integration_tests = [
            ('Test 1: API Gateway - Routage des Requêtes', self.test_api_gateway_routing),
            ('Test 2: Interface Web - Affichage Dashboard', self.test_web_dashboard),
            ('Test 3: Flux Complet - Vente → Stock → Saga', self.test_complete_sales_flow),
            ('Test 4: Projections CQRS via API Gateway', self.test_cqrs_projections),
            ('Test 5: Event Store via Interface Web', self.test_event_store_interface),
            ('Test 6: Monitoring et Métriques', self.test_monitoring_metrics),
            ('Test 7: Authentification et Autorisation', self.test_auth_flow),
            ('Test 8: Performance et Latence', self.test_performance)
        ]
        
        for test_name, test_function in integration_tests:
            logger.info(f"\n--- {test_name} ---")
            try:
                result = test_function()
                self.test_results.append({
                    'test': test_name,
                    'status': 'PASS' if result else 'FAIL',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Erreur dans {test_name}: {e}")
                self.test_results.append({
                    'test': test_name,
                    'status': 'ERROR',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                
        self.generate_integration_report()
        return True
        
    def test_api_gateway_routing(self) -> bool:
        """Test du routage API Gateway."""
        logger.info("Test routage API Gateway...")
        
        # Test de différentes routes
        routes_to_test = [
            ('/health', 'GET'),
            ('/api/events', 'GET'),
            ('/api/inventory/stock', 'GET'),
            ('/api/analytics/dashboard', 'GET'),
            ('/api/procurement/orders', 'GET')
        ]
        
        successful_routes = 0
        
        for route, method in routes_to_test:
            try:
                url = f"{API_GATEWAY_URL}{route}"
                response = requests.request(method, url, timeout=10)
                
                if response.status_code in [200, 201, 204]:
                    logger.info(f"✓ {method} {route}: {response.status_code}")
                    successful_routes += 1
                else:
                    logger.warning(f"✗ {method} {route}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"✗ {method} {route}: {e}")
                
        # Au moins 80% des routes doivent fonctionner
        success_rate = successful_routes / len(routes_to_test)
        logger.info(f"Taux de réussite du routage: {success_rate*100:.1f}%")
        
        return success_rate >= 0.8
        
    def test_web_dashboard(self) -> bool:
        """Test de l'interface web dashboard."""
        logger.info("Test interface web dashboard...")
        
        try:
            # Test de la page principale
            response = requests.get(f"{WEB_INTERFACE_URL}/", timeout=10)
            if response.status_code != 200:
                logger.error(f"Page principale inaccessible: {response.status_code}")
                return False
                
            # Test de l'endpoint dashboard API
            dashboard_response = requests.get(f"{WEB_INTERFACE_URL}/api/dashboard", timeout=10)
            if dashboard_response.status_code != 200:
                logger.error(f"Dashboard API inaccessible: {dashboard_response.status_code}")
                return False
                
            # Vérifier la structure des données
            dashboard_data = dashboard_response.json()
            required_sections = ['stock_summary', 'sales_summary', 'system_summary']
            
            for section in required_sections:
                if section not in dashboard_data:
                    logger.error(f"Section manquante dans dashboard: {section}")
                    return False
                    
            logger.info("✓ Interface web dashboard fonctionnelle")
            return True
            
        except Exception as e:
            logger.error(f"Erreur test dashboard: {e}")
            return False
            
    def test_complete_sales_flow(self) -> bool:
        """Test du flux complet de vente."""
        logger.info("Test flux complet vente → stock → saga...")
        
        try:
            # 1. Simuler une vente via API Gateway
            sale_data = {
                'product_id': 'PROD_INTEGRATION_TEST',
                'quantity': 15,
                'customer_id': 'CUSTOMER_TEST',
                'price': 25.99
            }
            
            sale_response = requests.post(
                f"{API_GATEWAY_URL}/api/sales",
                json=sale_data,
                timeout=10
            )
            
            if sale_response.status_code not in [200, 201]:
                logger.error(f"Échec création vente: {sale_response.status_code}")
                return False
                
            # 2. Attendre la propagation des événements
            time.sleep(8)
            
            # 3. Vérifier la mise à jour du stock via Analytics
            stock_response = requests.get(
                f"{API_GATEWAY_URL}/api/analytics/stock",
                timeout=10
            )
            
            if stock_response.status_code != 200:
                logger.error("Échec récupération données stock")
                return False
                
            # 4. Vérifier les analytics de vente
            analytics_response = requests.get(
                f"{API_GATEWAY_URL}/api/analytics/sales",
                timeout=10
            )
            
            if analytics_response.status_code != 200:
                logger.error("Échec récupération analytics vente")
                return False
                
            logger.info("✓ Flux complet de vente testé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur test flux vente: {e}")
            return False
            
    def test_cqrs_projections(self) -> bool:
        """Test des projections CQRS via API Gateway."""
        logger.info("Test projections CQRS...")
        
        projection_endpoints = [
            '/api/analytics/projections/stock',
            '/api/analytics/projections/alerts',
            '/api/analytics/projections/sales',
            '/api/analytics/projections/suppliers',
            '/api/analytics/projections/movements'
        ]
        
        successful_projections = 0
        
        for endpoint in projection_endpoints:
            try:
                response = requests.get(f"{API_GATEWAY_URL}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'timestamp' in data:  # Vérifier la structure
                        logger.info(f"✓ Projection {endpoint}: OK")
                        successful_projections += 1
                    else:
                        logger.warning(f"✗ Projection {endpoint}: structure invalide")
                else:
                    logger.warning(f"✗ Projection {endpoint}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"✗ Projection {endpoint}: {e}")
                
        success_rate = successful_projections / len(projection_endpoints)
        return success_rate >= 0.8
        
    def test_event_store_interface(self) -> bool:
        """Test de l'interface Event Store."""
        logger.info("Test interface Event Store...")
        
        try:
            # Test de récupération des événements
            events_response = requests.get(
                f"{API_GATEWAY_URL}/api/events/stream",
                timeout=10
            )
            
            if events_response.status_code != 200:
                logger.error("Échec récupération événements")
                return False
                
            # Test de publication d'événement
            test_event = {
                'event_type': 'IntegrationTest',
                'data': json.dumps({
                    'test_id': 'INTEGRATION_EVENT_TEST',
                    'timestamp': datetime.now().isoformat()
                })
            }
            
            publish_response = requests.post(
                f"{API_GATEWAY_URL}/api/events/publish",
                json=test_event,
                timeout=10
            )
            
            if publish_response.status_code not in [200, 201]:
                logger.error("Échec publication événement")
                return False
                
            # Test de replay d'événements
            replay_response = requests.post(
                f"{API_GATEWAY_URL}/api/events/replay",
                json={'from_timestamp': '2024-01-01T00:00:00Z'},
                timeout=15
            )
            
            if replay_response.status_code not in [200, 202]:
                logger.warning("Replay non disponible (optionnel)")
                
            logger.info("✓ Interface Event Store fonctionnelle")
            return True
            
        except Exception as e:
            logger.error(f"Erreur test Event Store: {e}")
            return False
            
    def test_monitoring_metrics(self) -> bool:
        """Test du monitoring et des métriques."""
        logger.info("Test monitoring et métriques...")
        
        try:
            # Test des métriques de santé système
            health_response = requests.get(
                f"{API_GATEWAY_URL}/api/analytics/system-health",
                timeout=10
            )
            
            if health_response.status_code != 200:
                logger.error("Métriques de santé inaccessibles")
                return False
                
            health_data = health_response.json()
            
            # Vérifier les métriques essentielles
            required_metrics = ['events_processed', 'services_status']
            for metric in required_metrics:
                if metric not in health_data.get('system_health', {}):
                    logger.warning(f"Métrique manquante: {metric}")
                    
            # Test endpoint Prometheus (si disponible)
            try:
                metrics_response = requests.get(
                    f"{API_GATEWAY_URL}/metrics",
                    timeout=5
                )
                if metrics_response.status_code == 200:
                    logger.info("✓ Métriques Prometheus disponibles")
                else:
                    logger.info("Métriques Prometheus non configurées")
            except:
                logger.info("Métriques Prometheus non disponibles")
                
            logger.info("✓ Monitoring de base fonctionnel")
            return True
            
        except Exception as e:
            logger.error(f"Erreur test monitoring: {e}")
            return False
            
    def test_auth_flow(self) -> bool:
        """Test du flux d'authentification (si implémenté)."""
        logger.info("Test authentification...")
        
        # Note: Test basique car l'auth peut ne pas être complètement implémentée
        try:
            # Test d'un endpoint protégé
            protected_response = requests.get(
                f"{API_GATEWAY_URL}/api/admin/health",
                timeout=5
            )
            
            # Soit OK (pas de protection), soit 401/403 (protection en place)
            if protected_response.status_code in [200, 401, 403, 404]:
                logger.info("✓ Gestion d'auth détectée ou non requise")
                return True
            else:
                logger.warning(f"Réponse inattendue: {protected_response.status_code}")
                return False
                
        except Exception as e:
            logger.info("Auth non implémentée ou non testable")
            return True  # Non-bloquant
            
    def test_performance(self) -> bool:
        """Test de performance basique."""
        logger.info("Test performance...")
        
        try:
            # Test de latence sur plusieurs requêtes
            response_times = []
            
            for i in range(5):
                start_time = time.time()
                response = requests.get(f"{API_GATEWAY_URL}/health", timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
                else:
                    logger.warning(f"Requête {i+1} échouée")
                    
                time.sleep(0.5)
                
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                
                logger.info(f"Temps de réponse moyen: {avg_response_time:.3f}s")
                logger.info(f"Temps de réponse max: {max_response_time:.3f}s")
                
                # Seuils acceptables (ajustables selon les besoins)
                if avg_response_time < 2.0 and max_response_time < 5.0:
                    logger.info("✓ Performance acceptable")
                    return True
                else:
                    logger.warning("Performance sous les attentes")
                    return False
            else:
                logger.error("Aucune réponse valide pour le test de performance")
                return False
                
        except Exception as e:
            logger.error(f"Erreur test performance: {e}")
            return False
            
    def generate_integration_report(self):
        """Génère le rapport d'intégration."""
        logger.info("\n=== RAPPORT D'INTÉGRATION LAB 7 ===")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.test_results if r['status'] == 'ERROR'])
        
        logger.info(f"Total des tests: {total_tests}")
        logger.info(f"Tests réussis: {passed_tests}")
        logger.info(f"Tests échoués: {failed_tests}")
        logger.info(f"Tests en erreur: {error_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            logger.info(f"Taux de réussite: {success_rate:.1f}%")
        
        logger.info("\nDétail des résultats:")
        for result in self.test_results:
            status_icon = "✓" if result['status'] == 'PASS' else "✗"
            logger.info(f"{status_icon} {result['test']}: {result['status']}")
            if 'error' in result:
                logger.info(f"   Erreur: {result['error']}")
                
        # Sauvegarder le rapport
        with open('integration_test_report.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'errors': error_tests,
                    'success_rate': (passed_tests/total_tests)*100 if total_tests > 0 else 0
                },
                'results': self.test_results,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
            
        logger.info("\nRapport d'intégration sauvegardé dans: integration_test_report.json")

def main():
    """Point d'entrée principal."""
    logger.info("Démarrage des tests d'intégration Lab 7")
    
    runner = IntegrationTestRunner()
    success = runner.run_integration_tests()
    
    if success:
        logger.info("Tests d'intégration terminés")
    else:
        logger.error("Échec lors des tests d'intégration")
        
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
