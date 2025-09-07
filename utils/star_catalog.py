# utils/star_catalog.py
import pandas as pd

def get_star_catalog():
    stars_data = [
        {"name": "Chitrā (Spica)", "ra_h": 13.419889, "dec_deg": -11.161319, "mag": 0.97},
        {"name": "Lubdhaka / Mrigavyādha (Sirius)", "ra_h": 6.752477, "dec_deg": -16.716116, "mag": -1.46},
        {"name": "Agastya (Canopus)", "ra_h": 6.399192, "dec_deg": -52.695661, "mag": -0.74},
        {"name": "Svātī (Arcturus)", "ra_h": 14.261208, "dec_deg": 19.182416, "mag": -0.05},
        {"name": "Abhijit (Vega)", "ra_h": 18.615649, "dec_deg": 38.783691, "mag": 0.03},
        {"name": "Brahmaṛṣi (Capella)", "ra_h": 5.278155, "dec_deg": 45.997991, "mag": 0.08},
        {"name": "Mṛgaśīrṣa (Rigel)", "ra_h": 5.242298, "dec_deg": -8.201639, "mag": 0.12},
        {"name": "Bhādrapadā (Procyon)", "ra_h": 7.655033, "dec_deg": 5.225, "mag": 0.38},
        {"name": "Ārdrā (Betelgeuse)", "ra_h": 5.919529, "dec_deg": 7.407064, "mag": 0.42},
        {"name": "Rohiṇī (Aldebaran)", "ra_h": 4.598677, "dec_deg": 16.509302, "mag": 0.75},
        {"name": "Dhruva (Polaris)", "ra_h": 2.530301, "dec_deg": 89.264109, "mag": 1.98}
    ]
    
    return pd.DataFrame(stars_data)