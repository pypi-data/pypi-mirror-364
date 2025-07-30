# __init__.py for OceanCrow Voting System
# Version: 0.1.0
# Author: Sheldon Kenny Salmon (OceanCrow)
# Purpose: Initialize the package and expose key functions
# Note: Part of the AquaFlow Master Blueprint; test in non-critical systems.

from .ocean_crow_voting_system import run_voting_system

__version__ = "0.1.0"
__author__ = "Sheldon Kenny Salmon"
__license__ = "MIT"

__doc__ = """
OceanCrow Voting System - In-game community feature voting system.
Allows players to submit and vote on ideas via a Pygame UI.
Built with the AquaFlow Master Blueprint for adaptability.
Usage: from ocean_crow_voting_system import run_voting_system
       run_voting_system() # Start the voting system
"""

__note__ = "Test in non-critical systems; no support provided. Respect the code's origin."