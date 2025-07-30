# ocean_crow_qa_chat/__init__.py 
# Version: 0.1.1
# Author: Sheldon Kenny Salmon (OceanCrow)
# Purpose: Initialize the package and expose key functions
# Note: Part of the AquaFlow Master Blueprint; test in non-critical systems.

from .ocean_crow_qa_chat import run_qa_chat


__version__ = "0.1.1"
__author__ = "Sheldon Kenny Salmon"
__license__ = "MIT"

__doc__ = """
OceanCrow Q&A Chat - In-game developer-player Q&A system.
Allows players to submit questions and devs to respond via a Pygame UI.
Built with the AquaFlow Master Blueprint for adaptability.
Usage: from ocean_crow_qa_chat import run_qa_chat
       run_qa_chat() # Start as player
       # Dev mode requires password 'dev123' (toggle with 'D')
"""

__note__ = "Test in non-critical systems; no support provided. Respect the code's origin."