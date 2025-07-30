import unittest
from unittest.mock import patch, MagicMock
from sus_adk.providers.generic import GenericProvider
from sus_adk.session import Session

class TestGenericProvider(unittest.TestCase):
    @patch('sus_adk.providers.generic.requests.post')
    def test_generate(self, mock_post):
        # Arrange
        api_url = 'https://fake-llm.com/api/generate'
        provider = GenericProvider(api_url)
        session = Session({'sessionid': 'abc123'})
        prompt = 'Hello!'
        expected_response = {'result': 'Hi there!'}
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Act
        result = provider.generate(prompt, session)

        # Assert
        mock_post.assert_called_once_with(
            api_url,
            json={'prompt': prompt},
            cookies={'sessionid': 'abc123'}
        )
        self.assertEqual(result, expected_response)

if __name__ == '__main__':
    unittest.main() 