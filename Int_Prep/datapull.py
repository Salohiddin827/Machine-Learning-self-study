import requests
import pandas as pd
import matplotlib.pyplot as plt

url = "https://climate.go.kr/atlas/am/am/co2"

response = requests.get(url)
json_data = response.json()

# 1️⃣ CO2 data listini olish
co2_list = json_data["CO2"]

# 2️⃣ DataFrame ga aylantirish
df = pd.DataFrame(co2_list)

# 3️⃣ Sanani datetime ga o‘tkazish
df["OBS_DATE"] = pd.to_datetime(df["OBS_DATE"])

# 4️⃣ Faqat CO2_sdata ni numeric qilish
df["CO2_sdata"] = pd.to_numeric(df["CO2_sdata"], errors="coerce")

print("Clean DataFrame:")
print(df)

# 5️⃣ Plot chizish
plt.figure(figsize=(12, 6))
plt.plot(df["OBS_DATE"], df["CO2_sdata"])
plt.xlabel("Date")
plt.ylabel("CO2 (ppm)")
plt.title("Daily CO2 Concentration")
plt.grid(True)
plt.tight_layout()
plt.show()

# 6️⃣ Korrelyatsiya
corr = df[["CO2_sdata"]].corr()
print("\nCorrelation Matrix:")
print(corr)