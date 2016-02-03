"""Extract features under social constraints.

This module extracts features for participants during different social
modes inferred from bluetooth connection data. Modes are:
    1. Completely alone (no connections)
    2. Alone in public (shifting connections)
    3. In dyad (1 recurring person)
    4. In group (2 others or more)
"""