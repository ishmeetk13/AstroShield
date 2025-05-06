

AstroShield – Satellite Collision Prediction System
Space just got safer
AstroShield is a real-time satellite collision prediction web application designed to ensure space safety and sustainability. Built with a clean Streamlit interface, it fetches live TLE data, calculates collision risks, and provides actionable maneuver suggestions to avoid catastrophic events.

Features:
Live Satellite Data Fetching from Celestrak or file upload.
Collision Prediction using the SGP4 orbital model and Euclidean distance.
Time to Closest Approach calculations.
Maneuver Suggestions to avoid primary and secondary collisions.
Secondary Collision Chain Analysis post-maneuver.
Interactive UI with animations and expanding sidebar.

Tech Stack
Frontend:
Streamlit
Plotly

Backend & Logic:
sgp4 – Orbital propagation
numpy – Vector calculations
pandas – Data handling
requests – TLE fetching
datetime, random

How It Works & How to Use
1. Data Input: Fetch live TLE data from Celestrak or upload your own .txt TLE files.
2. Threshold Selection: Adjust collision risk threshold (in km) via sidebar.
3. Run Prediction: AstroShield identifies satellite pairs with high collision probability.
4. Visual Alerts: Animated alert box and fade-in cards show collision details.
5. Maneuver Suggestions: Suggested positional changes to prevent impact.
6. Secondary Analysis: Re-checks for possible chain collisions post-maneuver.

Track
Tech for Social Good
Open Innovation

Future Scope
Audio Alerts and notification
ML-Based Debris Pattern Forecasting:
Use machine learning to identify future high-risk zones based on 
historical debris patterns.
Machine Learning-based Maneuver Optimization: Smarter, fuel-efficient 
collision avoidance planning.
User Authentication & Custom Dashboards: For organization-specific 
monitoring.
Mobile App Interface: Expand accessibility for on-the-go tracking and alerts


Business & Impact
Environmental Benefit: Reduces orbital pollution and space debris risks.
Commercial Use: Space agencies, satellite companies, and startups can integrate AstroShield into mission planning.
Sustainability: Supports long-term safe access to space.


Deployment
https://astroshield-cqzchan72ekhygvjgtaxpw.streamlit.app/

Repository
https://github.com/ishmeetk13/AstroShield

Presentation
https://drive.google.com/file/d/1CAf-Hi4pnTac9fiedaQdEV0R0FE0tDJF/view?usp=drivesdk
