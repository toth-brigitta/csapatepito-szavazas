import streamlit as st
import pandas as pd
from datetime import date, timedelta
import unicodedata

# --- Oldal alapbeállításai ---
st.set_page_config(layout="wide", page_title="Csapatépítő Szavazás")

# --- Adatszerkezet inicializálása ---
# Ez biztosítja, hogy a szavazatok megmaradjanak a felhasználói interakciók között.
if 'votes' not in st.session_state:
    def hungarian_sort_key(s):
        # Ékezetek nélküli verziót készít a helyes rendezéshez
        return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')
    
    users_list = sorted([
        'Zsuzsi', 'Bogi', 'Marci', 'Reni', 'Nóri', 'Brigi', 'Szonja', 'Anna', 'Réka', 'Nusi', 'Ádám', 'Zsófi', 'Mariann', 'Gábor'
    ], key=hungarian_sort_key)
    
    st.session_state.users = users_list
    # A szavazatokat egy dictionary-ben tároljuk
    st.session_state.votes = {user: [] for user in users_list}

# --- Dátumok és magyar napok előkészítése ---
start_date = date(2024, 11, 10)
end_date = date(2024, 12, 10)
all_weekdays = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1) if (start_date + timedelta(days=i)).weekday() < 5]
day_map = {0: 'H', 1: 'K', 2: 'Sz', 3: 'Cs', 4: 'P'}
# Az oszlopnevek formázása a táblázathoz: '2024.11.11 (H)'
column_labels = [f"{d.strftime('%Y.%m.%d')} ({day_map[d.weekday()]})" for d in all_weekdays]

# --- Felhasználói felület (Frontend) ---
st.title('🗓️ Búcsúbuli és Csapatépítő Szavazás')
st.markdown("Pipáld ki a sorodban a neked megfelelő napokat! A rendszer automatikusan menti a változást.")

# --- Névsor előkészítése a kiemeléshez ---
styled_users = []
for user in st.session_state.users:
    # Ha a felhasználónak nincs szavazata, piros pöttyöt kap
    if not st.session_state.votes.get(user, []):
        styled_users.append(f"🔴 {user}")
    else:
        styled_users.append(user)

# --- Interaktív Szavazó Táblázat ---
# Készítünk egy DataFrame-et a szavazatokból, ahol az értékek True/False (pipa)
df_for_editing = pd.DataFrame(False, index=styled_users, columns=column_labels)
for i, user_styled in enumerate(styled_users):
    user_original = user_styled.replace("🔴 ", "") # Visszaalakítás az eredeti névre
    user_votes = st.session_state.votes.get(user_original, [])
    for j, day in enumerate(all_weekdays):
        if day in user_votes:
            df_for_editing.iloc[i, j] = True

# Összegző sor kiszámítása és DataFrame-mé alakítása
summary_counts = df_for_editing.sum().astype(int).to_frame().T
summary_counts.index = ["ÖSSZES SZAVAZAT"]

# Az összegző sor megjelenítése (nem szerkeszthető)
st.dataframe(summary_counts)

# A szerkeszthető táblázat megjelenítése a felhasználóknak
edited_df = st.data_editor(df_for_editing, height=(len(st.session_state.users) + 1) * 36)

# --- Adatok visszaírása a szerkesztés után ---
# Amikor a felhasználó módosít valamit, az edited_df frissül,
# és mi visszaírjuk az adatokat a session_state-be.
for user_styled in edited_df.index:
    user_original = user_styled.replace("🔴 ", "")
    new_user_votes = []
    for i, is_checked in enumerate(edited_df.loc[user_styled]):
        if is_checked:
            new_user_votes.append(all_weekdays[i])
    st.session_state.votes[user_original] = new_user_votes