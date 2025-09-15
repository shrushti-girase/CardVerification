# import pandas as pd
# import firebase_admin
# from firebase_admin import credentials, db

# # Step 1: Load Firebase credentials
# cred = credentials.Certificate("cardholderform.json")  
# firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://cardholderform-default-rtdb.firebaseio.com/'
# })

# # Step 2: Load Excel file
# df = pd.read_excel("cardholder_data_indian.xlsx")

# # Optional: clean column names
# df.columns = df.columns.str.strip()

# # Step 3: Reference to /cards in Firebase
# cards_ref = db.reference("cards")

# # Step 4: Push each record
# for index, row in df.iterrows():
#     entry = {
#         "name": row["Name"],
#         "card_number": str(row["Card Number"]).replace(" ", ""),
#         "cvv": str(row["CVV"]).zfill(3),
#         "birthdate": str(row["Birthdate"])[:10],  # YYYY-MM-DD
#         "expiry": str(row["Expiry"])[:7]          # YYYY-MM
#     }
#     cards_ref.push(entry)

# print("✅ All Excel records uploaded to Firebase.")
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd

# Initialize Firebase
cred = credentials.Certificate("cardholderform.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cardholderform-default-rtdb.firebaseio.com/'
})

# Read the Excel file
df = pd.read_excel("cardholder_data_indian.xlsx")

# OPTIONAL: print headers to debug
print("Detected columns:", df.columns.tolist())

# Upload each row to Firebase
ref = db.reference('/')

for index, row in df.iterrows():
    data = {
        "name": row["name"],
        "card_number": str(row["card_number"]),
        "cvv": str(row["cvv"]),
        "birthdate": row["birthdate"],
        "expiry": row["expiry"]
    }
    ref.push(data)

print("✅ Upload complete.")
