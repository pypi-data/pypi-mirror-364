import unittest
from sus_adk.agent import Agent
from sus_adk.session import Session
from sus_adk.provider import BaseProvider

class MockProvider(BaseProvider):
    def generate(self, prompt, session, **kwargs):
        return f"{prompt} | cookies: {session.as_dict()} | kwargs: {kwargs}"

class TestAgent(unittest.TestCase):
    def test_agent_run(self):
        provider = MockProvider()
        session = Session({'token': 'abc'})
        agent = Agent(provider, session)
        result = agent.run('Test prompt', foo='bar')
        self.assertIn('Test prompt', result)
        self.assertIn('token', result)
        self.assertIn('foo', result)

    def test_agent_default_session(self):
        provider = MockProvider()
        agent = Agent(provider)
        result = agent.run('Prompt')
        self.assertIn('Prompt', result)
        self.assertIn('cookies: {}', result)

    def test_agent_provider_error(self):
        class FailingProvider(BaseProvider):
            def generate(self, prompt, session, **kwargs):
                raise RuntimeError('fail')
        agent = Agent(FailingProvider())
        with self.assertRaises(RuntimeError):
            agent.run('fail')

if __name__ == '__main__':
    unittest.main() 