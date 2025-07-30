# OceanCrow Q&A Chat
## Version: 0.1.1
## Author: Sheldon Kenny Salmon (OceanCrow)

### Overview
🌊 *OceanCrow Q&A Chat* hosts live Q&A sessions where devs answer player questions via a Pygame UI. Players submit questions, devs respond during events, and archives are saved. Built with the *AquaFlow Master Blueprint* for adaptability across industries (e.g., gaming, customer support).

### Installation
```bash
pip install ocean-crow-qa-chat
Usage
Run the System:
qa-chat
A window pops up. Type a question and press Enter to submit (5s cooldown) in Player Mode. Press 'D' to toggle to Dev Mode (enter password 'dev123'), then submit answers. Press 'A' to view archives. Times out after 60s.
Check Q&A:
Questions and answers save to qa_data_*.json. View the latest 5 on-screen or all in archive mode.
Tweak It:
Modify qa_data_*.json or extend the code.
Features
Simple UI for question submission and dev responses.
Saves Q&A data with locking and backups.
Displays top 5 Q&A pairs, with archive toggle.
Supports player and password-protected dev modes.
Shows next scheduled event.
License
MIT License - See LICENSE file.
Notes
Test in non-critical systems.
No support provided—experiment and adapt!