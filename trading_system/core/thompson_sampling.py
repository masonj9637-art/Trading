import numpy as np
import redis
import json

class ThompsonSampler:
    def __init__(self, agents, redis_host='localhost', redis_port=6379, regime="DEFAULT"):
        self.agents = agents  # e.g., ["chronos", "momentum", "order_flow", "sentiment"]
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.regime = regime
        self._initialize_state()
        
    def _get_key(self, agent_name):
        return f"thompson:beta:{self.regime}:{agent_name}"
        
    def _initialize_state(self):
        for agent in self.agents:
            key = self._get_key(agent)
            if not self.redis.exists(key):
                # Beta(1, 1) uniform prior for starting state
                self.redis.set(key, json.dumps({"alpha": 1, "beta": 1}))
                
    def set_regime(self, regime: str):
        self.regime = regime
        self._initialize_state()
                
    def sample_weights(self):
        """
        Samples from the Beta distribution for each agent to determine dynamic trust weighting.
        Assigns the highest capital allocation weight to the agent producing the highest sampled probability.
        """
        samples = {}
        for agent in self.agents:
            key = self._get_key(agent)
            state = json.loads(self.redis.get(key))
            # Sample from Beta(alpha, beta)
            samples[agent] = np.random.beta(state["alpha"], state["beta"])
            
        # As per spec: assign highest capital allocation weight to the agent producing highest sampled probability
        best_agent = max(samples, key=samples.get)
        
        # We will create a discrete allocation where the winning agent gets 1.0 weight and others get 0,
        # or we could normalize. Let's provide a normalized continuous distribution so they act as multipliers.
        total = sum(samples.values())
        weights = {agent: prob / total for agent, prob in samples.items()}
        
        # Or strict winner-takes-all:
        # weights = {agent: 1.0 if agent == best_agent else 0.0 for agent in self.agents}
        
        return weights, best_agent
        
    def update_prior(self, agent_name, profit_outcome: bool):
        """
        Update Beta priors based on binary trade outcomes.
        profit_outcome: True if profit, False if loss
        """
        key = self._get_key(agent_name)
        state = json.loads(self.redis.get(key))
        if profit_outcome:
            state["alpha"] += 1
        else:
            state["beta"] += 1
        self.redis.set(key, json.dumps(state))
