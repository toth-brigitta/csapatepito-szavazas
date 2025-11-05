import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches
from datetime import date, timedelta
import unicodedata

# --- Alapbeállítások és adatszerkezet ---

# Az alkalmazás "memóriájának" inicializálása
# Ez biztosítja, hogy a szavazatok megmaradjanak, amíg a felhasználók kattintgatnak
if 'votes' not in st.session_state:
    def hungarian_sort_key(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')
    
    users_list = sorted([
        'Zsuzsi', 'Bogi', 'Marci', 'Reni', 'Nóri', 'Brigi', 'Szonja', 'Anna', 'Réka', 'Nusi', 'Ádám', 'Zsófi', 'Mariann', 'Gábor'
    ], key=hungarian_sort_key)
    
    st.session_state.users = users_list
    st.session_state.votes = {user: [] for user in users_list}

start_date = date(2024, 11, 10)
end_date = date(2024, 12, 10)
all_weekdays = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1) if (start_date + timedelta(days=i)).weekday() < 5]

# --- Oldal felépítése (ez a Frontend) ---

st.set_page_config(layout="wide") # Szélesebb elrendezés
st.title('🗓️ Búcsúbuli és Csapatépítő Szavazás')
st.markdown("<p><b>1.</b> Válaszd ki a neved. <b>2.</b> Jelöld be a neked megfelelő napokat. <b>3.</b> Kattints a 'Szavazok!' gombra.</p>", unsafe_allow_html=True)

# Névválasztó legördülő menü
selected_user = st.selectbox('Kiválasztott név:', st.session_state.users)

# Dátumválasztó (több opcióval)
user_current_votes_str = [d.strftime('%Y-%m-%d (%a)') for d in st.session_state.votes[selected_user]]
options_str = [d.strftime('%Y-%m-%d (%a)') for d in all_weekdays]

selected_dates_str = st.multiselect(
    'Neked megfelelő időpontok:',
    options=options_str,
    default=user_current_votes_str
)

# Gomb a szavazat rögzítéséhez
if st.button('✅ Szavazok!'):
    # A string formátumú dátumokat visszaalakítjuk date objektumokká
    selected_dates = [date.fromisoformat(s[:10]) for s in selected_dates_str]
    st.session_state.votes[selected_user] = selected_dates
    st.success(f'{selected_user} szavazatait sikeresen rögzítettük!')

st.markdown("---")
st.subheader("📊 Jelenlegi állás")


# --- Ábra kirajzolása (ez a Backend logika) ---

def create_chart(votes_dict):
    df_users = pd.DataFrame(0, index=st.session_state.users, columns=all_weekdays)
    for voter, voted_dates in votes_dict.items():
        for voted_date in voted_dates:
            if voted_date in df_users.columns:
                df_users.loc[voter, voted_date] = 1

    summary_series = df_users.sum()
    df_summary = pd.DataFrame([summary_series], index=['ÖSSZES SZAVAZAT'])
    df = pd.concat([df_summary, df_users])

    fig, ax = plt.subplots(figsize=(18, 10))

    votes_matrix = df.iloc[1:, :]
    ax.imshow(votes_matrix, cmap=plt.get_cmap('Greens', 2), aspect='auto', interpolation='nearest', vmin=0, vmax=1,
              extent=[-0.5, len(all_weekdays)-0.5, len(st.session_state.users)-0.5, -0.5])
              
    rect = patches.Rectangle((-0.5, -0.5), len(all_weekdays), 1, linewidth=0, edgecolor='none', facecolor='#f0f0f0', zorder=0)
    ax.add_patch(rect)
    
    for j, count in enumerate(df.iloc[0, :]):
        if int(count) > 0:
            ax.text(j, 0, int(count), ha='center', va='center', color='black', fontweight='bold', fontsize=12)

    ax.set_xticks(range(len(all_weekdays)))
    ax.set_xticklabels([d.strftime('%m-%d\n%a') for d in all_weekdays])
    ax.set_yticks(range(len(df.index)))
    ax.set_yticklabels(df.index, fontsize=10)
    ax.invert_yaxis()

    ax.set_xticks([x + 0.5 for x in range(len(all_weekdays))], minor=True)
    ax.set_yticks([y + 0.5 for y in range(len(df.index)-1)], minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=2)
    ax.tick_params(which='minor', bottom=False, left=False)
    
    fig.tight_layout()
    return fig

# Az ábra megjelenítése az oldalon
st.pyplot(create_chart(st.session_state.votes))