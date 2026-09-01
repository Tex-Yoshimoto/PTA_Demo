import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import date

# 1. Googleスプレッドシートへの接続設定
def init_connection():
    # StreamlitのSecrets機能から認証情報を安全に取得する
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # ローカルテスト時はst.secrets、またはJSONファイルを直接読み込むように切り替え可能
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # ローカル確認用（環境に合わせて調整してください）
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        
    client = gspread.authorize(creds)
    
    # スプレッドシート名（またはID）を指定して開く
    # ※あらかじめ作成したスプレッドシート名に書き換えてください
    spreadsheet_id = "1YIxlFe9gix5S-S_tN8ySvAz8RIx89kR3kx5nfgchWTo"
    sheet = client.open_by_key(spreadsheet_id).sheet1
    return sheet

sheet = init_connection()

st.title("🏫 PTA 旗振り当番 予約システム")
st.markdown("希望する日時を選んで予約してください。")

# 2. 予約入力フォーム
with st.form("reservation_form"):
    st.subheader("新規予約の入力")
    
    # 日付選択（例：今日から1ヶ月先まで）
    target_date = st.date_input("希望日", value=date.today())
    
    # 時間帯の選択
    time_slot = st.selectbox(
        "時間帯",
        ["登校時（7:30〜8:15）", "下校時（15:00〜15:45）"]
    )
    
    # 学年・組、氏名
    grade_class = st.text_input("学年・組（例: 2年1組）")
    parent_name = st.text_input("保護者氏名")
    child_name = st.text_input("児童氏名")
    
    submitted = st.form_submit_button("予約を確定する")

    if submitted:
        if grade_class and parent_name:
            # スプレッドシートに1行追加
            sheet.append_row([
                str(target_date),
                time_slot,
                grade_class,
                parent_name,
                child_name
            ])
            st.success("予約が完了しました！ご協力ありがとうございます。")
        else:
            st.warning("「学年・組」と「保護者氏名」は必須です。")

st.divider()

# 3. 現在の予約状況一覧の表示
st.subheader("📅 現在の予約状況一覧")
try:
    data = sheet.get_all_records()
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("まだ予約はありません。")
except Exception as e:
    st.error(f"データを取得できませんでした: {e}")