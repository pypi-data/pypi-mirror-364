import unittest
from sus_adk.chain import Chain

class TestChain(unittest.TestCase):
    def test_chain_simple(self):
        chain = Chain([
            lambda x: x + 1,
            lambda x: x * 2
        ])
        result = chain.run(3)
        self.assertEqual(result, 8)  # (3+1)*2 = 8

    def test_chain_with_agent_mock(self):
        class MockAgent:
            def run(self, prompt):
                return f"Echo: {prompt}"
        agent = MockAgent()
        chain = Chain([
            lambda x: agent.run(f"Step1: {x}"),
            lambda x: agent.run(f"Step2: {x}")
        ])
        result = chain.run("input")
        self.assertEqual(result, "Echo: Step2: Echo: Step1: input")

    def test_chain_error_propagation(self):
        def fail_step(x):
            raise ValueError("fail")
        chain = Chain([
            lambda x: x + 1,
            fail_step,
            lambda x: x * 2
        ])
        with self.assertRaises(ValueError):
            chain.run(1)

if __name__ == '__main__':
    unittest.main() 