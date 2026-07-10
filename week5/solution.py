"""
============================================================================
  OPTIMIZED WORKSPACE  —  Truth Arena (The Membrane Strategy)
============================================================================
"""

import numpy as np
from truth import TruthRule, run

# REQUIRED: The design note is injected into the weights file.
NOTE = "Our society survives by forming a highly cohesive outer membrane, prioritizing dense clustered growth to maximize the 'truth' neighbor immunity threshold against liar conversion cascades."

# ===========================================================================
#  SECTION 1: THE FITNESS FUNCTION
# ===========================================================================
def how_good_is(rule):
    total = 0.0
    # Testing on 5 seeds instead of 4 prevents the model from overfitting to one map layout.
    for seed in range(5):                 
        r = run(rule, seed=seed)
        
        # We aggressively exponentiate cohesion. 
        # A large society that is thin will score terribly.
        # A slightly smaller but impenetrable society will score massively.
        reward = r["size"] * (r["cohesion"] ** 2.5)
        total += reward

    return total / 5                      


# ===========================================================================
#  SECTION 2: THE SEARCH (Enhanced Genetic Algorithm)
# ===========================================================================
# Scaled up for a robust search (will take longer to run, but yields a stronger rule)
POP         = 32      # Larger population for more genetic diversity
GENERATIONS = 100     # More rounds to solidify the survival strategy
KEEP        = 6       # Elitism: how many top rules survive untouched
MUTATION    = 0.10    # Slightly tighter mutation for fine-tuning late generations

def find_best_rule():
    rng = np.random.default_rng(42)
    n = TruthRule().n_params

    # Start with a diverse group of random rules
    group = [rng.standard_normal(n).astype(np.float32) * 0.3 for _ in range(POP)]
    best_weights, best_score = None, -1.0

    for gen in range(GENERATIONS):
        # Score every rule
        scored = []
        for weights in group:
            rule = TruthRule().set_flat(weights)
            scored.append((how_good_is(rule), weights))
        
        # Rank them
        scored.sort(key=lambda pair: pair[0], reverse=True)

        # Track the all-time best
        if scored[0][0] > best_score:
            best_score, best_weights = scored[0][0], scored[0][1].copy()
        print(f"round {gen:3d}   best {scored[0][0]:.5f}")

        # Elitism: Keep the exact weights of our best performers
        winners = [w for _, w in scored[:KEEP]]
        next_group = list(winners) 

        # Repopulate using Crossover and Mutation
        while len(next_group) < POP:
            # Pick two random parents from the winners circle
            parent1 = winners[rng.integers(0, KEEP)]
            parent2 = winners[rng.integers(0, KEEP)]
            
            # Crossover: Mix their traits
            child = np.where(rng.random(n) > 0.5, parent1, parent2)
            
            # Mutate: Add random noise
            child += rng.standard_normal(n).astype(np.float32) * MUTATION
            next_group.append(child)
            
        group = next_group

    return TruthRule().set_flat(best_weights)


# ===========================================================================
#  EXECUTION
# ===========================================================================
if __name__ == "__main__":
    print("training your robust rule…")
    rule = find_best_rule()
    rule.save("my_rule", note=NOTE)
    print("\nsaved my_rule.npz")
    print("now run:  python check.py my_rule.npz")