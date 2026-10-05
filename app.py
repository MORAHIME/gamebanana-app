import re
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="GameBanana 정보 추출기", page_icon="🍌", layout="wide")

st.title("🍌 GameBanana Mod Info Extractor")
st.write("GameBanana 모드 URL을 아래에 입력하면 정보를 정리해 드립니다.")

urls_input = st.text_area(
    "URL 목록 입력 (한 줄에 하나씩)",
    height=150,
    placeholder="https://gamebanana.com/mods/718215"
)

def get_mod_info(url):
    url = url.strip()
    if not url:
        return None

    match = re.search(r'/mods/(\d+)', url)
    if not match:
        return {"URL": url, "Title": "N/A", "Submitter": "N/A", "Updates": "잘못된 URL"}
    
    mod_id = match.group(1)
    api_url = f"https://gamebanana.com/apiv3/Mod/{mod_id}/ProfilePage"
    
    try:
        response = requests.get(api_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code != 200:
            return {"URL": url, "Title": "N/A", "Submitter": "N/A", "Updates": f"HTTP {response.status_code}"}
        
        data = response.json()
        title = data.get("_sName", "제목 없음")
        submitter = data.get("_aSubmitter", {}).get("_sName", "작성자 없음")
        
        updates = []
        for u in data.get("_aUpdates", []):
            ver = u.get("_sVersion", "")
            t = u.get("_sTitle", "")
            updates.append(f"[{ver}] {t}".strip() if ver else t)
            
        return {
            "URL": url,
            "Title": title,
            "Submitter": submitter,
            "Updates": " / ".join(updates) if updates else "없음"
        }
    except Exception as e:
        return {"URL": url, "Title": "N/A", "Submitter": "N/A", "Updates": f"에러: {str(e)}"}

if st.button("🚀 정보 추출 시작", type="primary", use_container_width=True):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    if not urls:
        st.warning("URL을 입력하세요.")
    else:
        results = []
        prog = st.progress(0)
        for idx, u in enumerate(urls):
            res = get_mod_info(u)
            if res:
                results.append(res)
            prog.progress((idx + 1) / len(urls))
            
        df = pd.DataFrame(results)
        st.subheader("📋 결과")
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="💾 CSV 파일 다운로드",
            data=csv,
            file_name="gamebanana_mods.csv",
            mime="text/csv",
            use_container_width=True
        )
