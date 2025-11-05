import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta
import unicodedata

# --- Oldal alapbeállításai ---
st.set_page_config(layout="wide", page_title="Csapatépítő Szavazás")

# --- Adatszerkezet inicializálása a Session State-ben ---
# Ez biztosítja, hogy a szavazatok megmaradjanak a felhasználói interakciók között.
if 'votes' not in st.session_state:
    def hungarian_sort_key(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')
    
    users_list = sorted([
        'Zsuzsi', 'Bogi', 'Marci', 'Reni', 'Nóri', 'Brigi', 'Szonja', 'Anna', 'Réka', 'Nusi', 'Ádám', 'Zsófi', 'Mariann', 'Gábor'
    ], key=hungarian_sort_key)
    
    st.session_state.users = users_list
    st.session_state.votes = {user: [] for user in users_list}

# Dátumok és magyar napok előkészítése
start_date = date(2024, 11, 10)
end_date = date(2024, 12, 10)
all_weekdays = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1) if (start_date + timedelta(days=i)).weekday() < 5]
day_map = {0: 'H', 1: 'K', 2: 'Sz', 3: 'Cs', 4: 'P'}

# --- Felhasználói felület (Frontend) ---
st.title('🗓️ Búcsúbuli és Csapatépítő Szavazás')
st.markdown("<p><b>1.</b> Válaszd ki a neved a listából. <b>2.</b> A megjelenő táblázatban pipáld ki a neked megfelelő napokat!</p>", unsafe_allow_html=True)

selected_user = st.selectbox('Válassz a listából:', st.session_state.users)

st.markdown(f"**Szia {selected_user}! Kérlek, itt jelöld a szavazataidat:**")

# --- Interaktív Szavazó Táblázat ---
# A kiválasztott felhasználó szavazataiból készítünk egy DataFrame-et (True/False értékekkel)
current_user_votes = st.session_state.votes.get(selected_user, [])
data_for_editor = {d: [d in current_user_votes] for d in all_weekdays}
df_editor = pd.DataFrame(data_for_editor, index=[selected_user])

# A DataFrame oszlopainak formázása a jobb olvashatóságért (pl. '2024-11-11 (H)')
df_editor.columns = [f"{d.strftime('%Y.%m.%d')} ({day_map[d.weekday()]})" for d in all_weekdays]

# A szerkeszthető táblázat megjelenítése
edited_df = st.data_editor(df_editor, height=75)

# A szerkesztett adatok visszaírása a 'votes' szótárba
new_votes = []
for i, col_name in enumerate(edited_df.columns):
    # Ha a cella értéke (pipa) True, hozzáadjuk az eredeti dátumot a listához
    if edited_df[col_name].iloc[0]:
        new_votes.append(all_weekdays[i])
st.session_state.votes[selected_user] = new_votes


# --- Összesítő Ábra ---
st.markdown("---")
st.subheader("📊 Eredmények valós időben")

def create_chart(votes_dict):
    """Ez a függvény hozza létre az összesítő matplotlib ábrát."""
    df_users = pd.DataFrame(0, index=st.session_state.users, columns=all_weekdays)
    for voter, voted_dates in votes_dict.items():
        for voted_date in voted_dates:
            if voted_date in df_users.columns:
                df_users.loc[voter, voted_date] = 1

    summary_series = df_users.sum()
    df_summary = pd.DataFrame([summary_series], index=['ÖSSZES SZAVAZAT'])
    df = pd.concat([df_summary, df_users])

    fig, ax = plt.subplots(figsize=(20, 11)) # Méret növelése

    votes_matrix = df.iloc[1:, :]
    ax.imshow(votes_matrix, cmap=plt.get_cmap('Greens', 2), aspect='auto', interpolation='nearest', vmin=0, vmax=1,
              extent=[-0.5, len(all_weekdays)-0.5, len(st.session_state.users)-0.5, -0.5])
              
    ax.add_patch(plt.Rectangle((-0.5, -0.5), len(all_weekdays), 1, linewidth=0, edgecolor='none', facecolor='#f0f0f0'))
    
    for j, count in enumerate(df.iloc[0, :]):
        if int(count) > 0:
            ax.text(j, 0, int(count), ha='center', va='center', color='black', fontweight='bold', fontsize=12)

    # Dátum és nap formátum beállítása az X-tengelyen
    date_labels = [f"{d.strftime('%Y.%m.%d')}\n{day_map[d.weekday()]}" for d in all_weekdays]
    ax.set_xticks(range(len(all_weekdays)))
    ax.set_xticklabels(date_labels, fontsize=9)
    
    ax.set_yticks(range(len(df.index)))
    ax.set_yticklabels(df.index, fontsize=10)
    ax.invert_yaxis()

    ax.set_xticks([x + 0.5 for x in range(len(all_weekdays))], minor=True)
    ax.set_yticks([y + 0.5 for y in range(len(df.index)-1)], minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=2.5)
    ax.tick_params(which='minor', bottom=False, left=False)
    
    fig.tight_layout()
    return fig

# Az ábra megjelenítése
st.pyplot(create_chart(st.session_state.votes))