import unittest
from doctorcheck.health_logic import evaluate_health

class TestHealthLogic(unittest.TestCase):
    def test_normal_health(self):
        result = evaluate_health(30, 120, 80, False, False)
        self.assertEqual(result, "Votre santé semble normale basée sur les informations fournies.")

    def test_high_bp(self):
        result = evaluate_health(40, 150, 95, False, False)
        self.assertEqual(result, "Hypertension modérée. Une consultation médicale est recommandée.")

    def test_symptoms(self):
        result = evaluate_health(25, 120, 80, True, True)
        self.assertEqual(result, "Symptômes préoccupants (maux de tête et fatigue). Consultez un médecin.")

if __name__ == "__main__":
    unittest.main()
