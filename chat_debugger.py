### 必要な標準ライブラリをインポートする
import copy
import chardet  # 文字コードの判定
import os
import math     # nanの判定（math.isnan）
import json

### 必要な外部ライブラリをインポートする
import streamlit as st
import streamlit.components.v1 as stc
import numpy as np
import pandas as pd


### 自作のモジュールをインポートする
import func_html_lab


def st_display_table(df: pd.DataFrame):
    """
    Streamlitでデータフレームを表示する関数
    
    Parameters
    ----------
    df : pd.DataFrame
        対象のデータフレーム

    Returns
    -------
    なし
    """

    # データフレームを表示
    st.subheader('データの確認')
    st.table(df)

    # 参考：Streamlitでdataframeを表示させる | ITブログ
    # https://kajiblo.com/streamlit-dataframe/


def view_lesson():

    ### 各種フラグなどを初期化するセクション ###
    if 'init_flg' not in st.session_state:

        st.session_state['init_flg'] = True         # 初期化(済)フラグをオンに設定
        st.session_state['list_csv'] = []           # csvのリスト
        st.session_state['check_flg'] = False       # csv初期検査の実行済フラグ
        st.session_state['count_page'] = 0          # 表示しているページ数        
        # st.session_state['error_flg'] = False       # csv初期検査のエラーフラグ

    if st.session_state['check_flg'] == False:

        # ファイルアップローダー
        uploaded_file = st.file_uploader('CSVファイルをドラッグ＆ドロップしてください', type=['csv'])

        # アップロードの有無を確認
        if uploaded_file is not None:

            # 文字コードの判定
            stringio = uploaded_file.getvalue()
            enc = chardet.detect(stringio)['encoding']
            # print(enc)

            # データフレームの読み込み
            df = pd.read_csv(uploaded_file, encoding=enc) 
            df.index = np.arange(1, len(df)+1)

            # データフレームをリストに変換
            list_csv = df.to_numpy().tolist()
            st.session_state['list_csv'] = list_csv

            error_flg = False

            try:
                for idx, line in enumerate(list_csv):

                    # text列のチェック
                    for text in line[4]:
                        # print(f'{text} = {ord(text)}')

                        if ord(text) == 10:
                            st.warning(f'{idx+1} 行目の text 列に改行が含まれています')
                            error_flg = True

                    # style列のチェック
                    styles = ['free', 'left', 'right', 'photo', 'video', 'pickL', 'pickL3', 'pickR', 'pickR3', 'pickP', 'pickP3', 'pickV', 'pickV3',]
                    if line[1] not in styles:
                        st.warning(f'{idx+1} 行目の style 列に不正な値が設定されています')
                        error_flg = True

                    if isinstance(line[5], str):
                        if len(line[5]) == 0:
                            st.warning(f'{idx+1} 行目の res1 列が入力されていません ※必須入力')
                            error_flg = True

                    if isinstance(line[5], float):
                        if math.isnan(line[5]) == True:
                            st.warning(f'{idx+1} 行目の res1 列が入力されていません ※必須入力')
                            error_flg = True

                
            except Exception as e:

                print(f'エラー : {e}')
                error_flg = True


            if error_flg == True:
                st.error(f'CSVデータにエラーが見つかりました。修正して再アップロードしてください。')

                # テーブルの表示
                st_display_table(df)

            else:
                st.success(f'CSVデータが正常に読み込めました。ボタンを押してプレビュー画面に進んでください。')
                st.session_state['check_flg'] = True

                if st.button('チャットのプレビュー'):
                    pass

    else:

        list_csv = st.session_state['list_csv']
        page = st.slider('表示するページを指定してください（スライダーにフォーカスを当てた後は、カーソルキーで移動できます）', min_value=1, max_value=len(list_csv))
        idx = page -1

        text_html = func_html_lab.make_html_balloon(str(list_csv[idx][2]), func_html_lab.trans_html_tag(str(list_csv[idx][4])))
        stc.html(text_html, height=200)
        st.write(f'【話者】 {list_csv[idx][3]}')

        st.radio('【選択肢】', [list_csv[idx][5], list_csv[idx][6]])

        st.write('')
        st.write('【csvファイル詳細】')
        st.write(list_csv[idx])


        # for idx, line in enumerate(list_csv):
        #     pass

        st.sidebar.caption('機能')
        col = st.sidebar.columns([7,3])

        if col[0].button('別なCSVを読込みなおす'):
            del st.session_state['init_flg']    # セッションステートの削除
            st.sidebar.info('デバッガを初期化しました。《再読込》ボタンをクリックしてください。')
            uploaded_file = None
            col[1].button('再読込')

        export_file_name = st.sidebar.text_input('JSONファイル名', placeholder='例： it01-01-c1 、 it01-01-c2 など')
        export_button = st.sidebar.button('CSVファイルをJSON形式に変換する')

        if export_button:
            if not export_file_name:
                st.sidebar.warning('JSONファイル名を入力してください')

            dict_json = {}
            dict_json['scene'] = export_file_name
            dict_json['datas'] = []

            for idx, line in enumerate(list_csv):

                dict_temp = {}
                dict_temp['id']    = str(line[0])
                dict_temp['style'] = str(line[1])
                dict_temp['img']   = str(line[2])
                dict_temp['name']  = str(line[3])
                dict_temp['text']  = str(line[4])
                dict_temp['res1']  = str(line[5])
                dict_temp['res2']  = str(line[6])

                if dict_temp['res2'] == 'nan':
                    dict_temp['res2'] = ''

                dict_json['datas'].append(dict_temp)

            # json_path = './temp/' + str(export_file_name) + '.json'
            # json_file = open(json_path, mode='w', encoding='utf-8')
            # json.dump(dict_json, json_file, indent=4, ensure_ascii=False)
            # json_file.close()


            json_string = json.dumps(dict_json, indent=4, ensure_ascii=False)

            st.sidebar.download_button(
                label="JSONファイルをダウンロードする",
                file_name=str(export_file_name)+'.json',
                mime="application/json",
                data=json_string,
            )
