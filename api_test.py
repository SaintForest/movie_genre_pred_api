import unittest
from unittest.mock import patch
import concurrent.futures


from api import app, analyze_data, get_model


class APITestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_analyze_data_single_genre_valid_description(self):
        with self.app as client:
            response = client.post('/analyze', data={'description': 'a comedy movie about students partying in a island'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"['Comedy']", response.data)
        print("Test 'test_analyze_data_single_genre_valid_description' passed.")

    def test_analyze_data_multiple_genre_valid_description(self):
        with self.app as client:
            response = client.post('/analyze', data={'description': 'a horror comedy movie about students partying in a island'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"['Comedy', 'Horror']", response.data)
        print("Test 'test_analyze_data_multiple_genre_valid_description' passed.")

    
    def test_analyze_data_not_suitable_description(self):
        with self.app as client:
            response = client.post('/analyze', data={'description': 'random random'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"No suitable genre found for the given description", response.data)
        print("Test 'test_analyze_data_not_suitable_description' passed.")


    def test_analyze_data_missing_description(self):
        with self.app as client:
            response = client.post('/analyze')
            self.assertEqual(response.status_code, 400)
            self.assertIn(b'Missing required field', response.data)
        print("Test 'test_analyze_data_missing_description' passed.")

    def test_analyze_data_invalid_description(self):
        with self.app as client:
            response = client.post('/analyze', data={'description': 'Invalid !@#$ description'})
            self.assertEqual(response.status_code, 400)
            self.assertIn(b'Title and description have non-alphanumeric characters', response.data)
        print("Test 'test_analyze_data_invalid_description' passed.")

    @patch('api.get_model')
    def test_analyze_data_exception(self, mock_get_model):
        mock_get_model.side_effect = Exception('Model loading error')
        with self.app as client:
            response = client.post('/analyze', data={'description': 'Valid description'})
            self.assertEqual(response.status_code, 500)
            self.assertIn(b'Model loading error', response.data)
        print("Test 'test_analyze_data_exception' passed.")

    def test_handle_get_request(self):
        with self.app as client:
            response = client.get('/analyze')
            self.assertEqual(response.status_code, 405)
            self.assertIn(b'Method not allowed', response.data)
        print("Test 'test_handle_get_request' passed.")
    
    def test_analyze_data_long_description(self):
        with self.app as client:
            description = 'a' * 2000  # Generate a description longer than the maximum allowed length
            response = client.post('/analyze', data={'description': description})
            self.assertEqual(response.status_code, 400)
            self.assertIn(b'Description argument is too large', response.data)
        print("Test 'test_analyze_data_long_description' passed.")
    
    def test_analyze_data_short_description(self):
        with self.app as client:
            description = 'a'   # Generate a description shorter than the minimum allowed length
            response = client.post('/analyze', data={'description': description})
            self.assertEqual(response.status_code, 400)
            self.assertIn(b'Description argument is less than 10', response.data)
        print("Test 'test_analyze_data_short_description' passed.")


    def test_invalid_endpoint(self):
        with self.app as client:
            response = client.get('/invalid')
            self.assertEqual(response.status_code, 404)
            self.assertIn(b'Endpoint not found', response.data)
        print("Test 'test_invalid_endpoint' passed.")

    def test_invalid_request_method(self):
        with self.app as client:
            response = client.put('/analyze')
            self.assertEqual(response.status_code, 405)
            self.assertIn(b'Method not allowed', response.data)
        print("Test 'test_invalid_request_method' passed.")

    def test_analyze_data_case_sensitive_endpoint(self):
        with self.app as client:
            response = client.post('/Analyze', data={'description': 'a comedy movie about students partying in a island'})
            self.assertEqual(response.status_code, 404)
            self.assertIn(b'Endpoint not found', response.data)
        print("Test 'test_analyze_data_case_sensitive_endpoint' passed.")

    def test_analyze_data_large_number_of_requests(self):
        # Simulate a large number of requests to check for performance and stability
        for _ in range(30):
            with self.app as client:
                response = client.post('/analyze', data={'description': 'a comedy movie'})
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"['Comedy']", response.data)
        print("Test 'test_analyze_data_large_number_of_requests' passed.")

    def test_analyze_data_concurrent_requests(self):
        def send_request():
            with self.app as client:
                response = client.post('/analyze', data={'description': 'a comedy movie'})
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"['Comedy']", response.data)

        # Simulate concurrent requests
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(send_request) for _ in range(10)]

            # Wait for all requests to complete
            concurrent.futures.wait(futures)

        print("Test 'test_analyze_data_concurrent_requests' passed.")

    def test_analyze_data_maximum_payload(self):
        # Test the maximum payload size that the API can handle
        description = 'fun' * 333  # Generate a description of the maximum allowed length
        with self.app as client:
            response = client.post('/analyze', data={'description': description})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"['Drama']", response.data)
        print("Test 'test_analyze_data_maximum_payload' passed.")




if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(APITestCase)
    unittest.TextTestRunner().run(suite)
