import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import os
import plotly.graph_objects as go

# 初始化Dash應用
app = dash.Dash(__name__)

# 獲取Flask伺服器
server = app.server 

# 讀取數據
def load_data():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        fb_path = os.path.join(current_dir, 'data', 'FB_all_data.xlsx')
        ig_path = os.path.join(current_dir, 'data', 'IG_all_data.xlsx')
        
        if not os.path.exists(fb_path) or not os.path.exists(ig_path):
            raise FileNotFoundError("數據文件不存在")
            
        fb_data = pd.read_excel(fb_path, sheet_name=None)
        ig_data = pd.read_excel(ig_path, sheet_name=None)
        
        # 定義 IG 欄位名稱
        ig_column_mapping = {
            '圖文': {
                '類別': '分類',
                '發布日期': '張貼日期',
                '發布時間': '張貼時間',
                '發布時': '發布小時',
                '永久連結': '發布網址',
                '觸及人數': '觸及數量',
                '按讚數': '按讚數量',
                '分享': '分享數量',
                '留言數': '留言數量',
                '分享率': '分享率別'
            },
            '限時動態': {
                '期間（秒）': '動態時間',
                '發布日期': '張貼日期',
                '發布時間': '張貼時間',
                '發布時': '發布小時',
                '觸及人數': '觸及數量',
                '按讚數': '按讚數量',
                '分享': '分享數量',
                '分享率': '分享率別'
            }
        }
        
        # 統一處理所有數值列
        numeric_cols = {
            'FB': {
                '貼文': ['觸及人數', '總點擊次數', '連結點擊次數', '心情', '留言', '分享'],
                '影片': ['心情', '影片觀看 3 秒以上的次數', '觸及人數', '留言', '分享']
            },
            'IG': {
                '圖文': ['觸及數量', '按讚數量', '分享數量', '留言數量', '珍藏次數', '分享率別']
            }
        }
        
        # 處理fb數據
        for sheet_name in fb_data:
            df = fb_data[sheet_name]
            if sheet_name in numeric_cols['FB']:
                for col in numeric_cols['FB'][sheet_name]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 處理日期
            if '發布日期' in df.columns:
                df['發布日期'] = pd.to_datetime(df['發布日期'], errors='coerce')
        
        # 處理IG數據
        for sheet_name in ig_data:
            df = ig_data[sheet_name]
            
            # 重新命名欄位
            if sheet_name in ig_column_mapping:
                df.rename(columns=ig_column_mapping[sheet_name], inplace=True)
            
            # 處理數值型columns
            if sheet_name in numeric_cols['IG']:
                for col in numeric_cols['IG'][sheet_name]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 處理日期列
            if '張貼日期' in df.columns:
                df['張貼日期'] = pd.to_datetime(df['張貼日期'], errors='coerce')
        
        return fb_data, ig_data
        
    except Exception as e:
        print(f"數據加載錯誤: {str(e)}")
        return {}, {}

fb_data, ig_data = load_data()

# 應用布局
app.layout = html.Div(style={
    'fontFamily': 'Arial',
    'maxWidth': '100%',
    'margin': '0 auto',
    'padding': '0 15px'  # 增加響應式padding
}, children=[
    # 標題
    html.H1('社群數據分析儀錶板',
            style={'textAlign': 'center', 
                   'color': '#f1f1f1', 
                   'padding': '10px',
                   'backgroundColor': '#225A3E',
                   'marginBottom': '24px'}),
    
    # 主要內容區域
    html.Div([
        # 左側選單區域 (1/3寬度)
        html.Div([
            html.H2("數據與圖示選單", style={'textAlign': 'center', 'color': '#202020', 'padding': '10px', 'backgroundColor': '#fbad3c', 'marginBottom': '10px'}),
            # 社群選擇
            html.H3('社群平台選擇'),
            dcc.Dropdown(
                id='platform-dropdown',
                options=[
                    {'label': 'Facebook', 'value': 'FB'},
                    {'label': 'Instagram', 'value': 'IG'}
                ],
                value='FB'
            ),
            
            # 數據類型選擇
            html.H3('數據類型選擇'),
            dcc.Dropdown(id='sheet-dropdown'),
            
            # 數據比對區域
            html.Div([
                html.H3('數據比對項目', style={'marginTop': '18px'}),
                html.Div([
                    # X軸和Y軸並排
                    html.Div([
                        html.Label('第一圖示X軸：', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                        dcc.Dropdown(
                            id='x-axis-dropdown',
                            options=[
                                {'label': '發布日期', 'value': '發布日期'},
                                {'label': '類別', 'value': '類別'},
                                {'label': '觸及人數', 'value': '觸及人數'}
                            ],
                            value='發布日期',
                            style={'width': '200px'}
                        ),
                    ], style={'display': 'inline-block', 'marginRight': '20px', 'width': '45%'}),
                    
                    html.Div([
                        html.Label('第一圖示Y軸：', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                        dcc.Dropdown(
                            id='y-axis-dropdown',
                            options=[
                                {'label': '總點擊次數', 'value': '總點擊次數'},
                                {'label': '觸及人數', 'value': '觸及人數'},
                                {'label': '發布日期', 'value': '布日期'},
                                {'label': '類別', 'value': '類別'}
                            ],
                            value='觸及人數',
                            style={'width': '200px'}
                        ),
                    ], style={'display': 'inline-block', 'width': '45%'}),
                ], style={'marginBottom': '15px', 'display': 'flex', 'justifyContent': 'space-between'}),
                
                # 第二張圖的控制選項
                html.Div([
                    html.Div([
                        html.Label('第二圖示X軸：', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                        dcc.Dropdown(
                            id='second-x-axis-dropdown',
                            options=[
                                {'label': '類別', 'value': '類別'},
                                {'label': '發布時間', 'value': '發布時間'}
                            ],
                            value='類別',
                            style={'width': '200px'}
                        ),
                    ], style={'display': 'inline-block', 'marginRight': '20px', 'width': '45%'}),
                    
                    html.Div([
                        html.Label('第二圖示Y軸：', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                        dcc.Dropdown(
                            id='second-y-axis-dropdown',
                            options=[
                                {'label': '觸及人數', 'value': '觸及人數'},
                                {'label': '分享', 'value': '分享'},
                                {'label': '留言', 'value': '留言'},
                                {'label': '心情', 'value': '心情'}
                            ],
                            value='觸及人數',
                            style={'width': '200px'}
                        ),
                    ], style={'display': 'inline-block', 'width': '45%'}),
                ], style={'marginBottom': '15px', 'display': 'flex', 'justifyContent': 'space-between'}),
            ], id='comparison-section', style={'display': 'none'}),
            
            # 左下角類別圓餅圖
            html.Div([
                html.H3('各類別所占比例', style={'marginTop': '20px'}),
                dcc.Graph(id='category-pie-chart')
            ], style={'marginTop': 'auto'})
            
        ], style={
            'width': '25%', 
            'minWidth': '300px',  # 設置最小寬度
            'float': 'left', 
            'padding': '20px',
            'backgroundColor': '#c5c5c3',
            'borderRadius': '10px',
            'marginRight': '20px',
            'height': 'calc(100vh - 150px)',
            'boxShadow': '2px 2px 5px rgba(0,0,0,0.1)',
            'display': 'flex',
            'flexDirection': 'column',
            '@media (max-width: 1200px)': {
                'width': '100%',
                'marginRight': '0',
                'marginBottom': '20px'
            }
        }),
        
        # 右側圖表區域
        html.Div([
            # 第一張圖表
            html.Div([
                dcc.Graph(
                    id='share-rate-graph',
                    style={'height': '40vh'}
                )
            ], style={
                'border': '1px solid #ddd',
                'borderRadius': '10px',
                'padding': '10px',
                'marginBottom': '20px',
                'backgroundColor': 'maroon',
                'boxShadow': '2px 2px 5px rgba(0,0,0,0.1)',
                'height': '41vh',
                'backgroundImage': 'url("/assets/background.jpg")',  # 添加背景圖片
                'backgroundSize': 'cover',
                'backgroundPosition': 'center',
                'display': 'block'  # 默認顯示
            }, id='first-graph-container'),
            
            # 第二張圖表
            html.Div([
                dcc.Graph(
                    id='reach-graph',
                    style={'height': '40vh'}
                )
            ], style={
                'border': '1px solid #ddd',
                'borderRadius': '10px',
                'padding': '10px',
                'backgroundColor': 'teal',
                'boxShadow': '2px 2px 5px rgba(0,0,0,0.1)',
                'height': '41vh',
                'display': 'block'  # 默認顯示
            }, id='second-graph-container'),
        ], style={
            'width': 'calc(75% - 40px)',
            'float': 'left',
            'marginLeft': '0px'
        }),
    ], style={
        'display': 'flex',
        'margin': '0 20px'
    }),
    
    # 最下方數據表格區域
    html.Div([
        html.H3(id='data-title', style={
            'textAlign': 'center',
            'color': '#225A3E',
            'marginBottom': '15px'
        }),
        # 添加下載按鈕
        html.Button(
            '下載數據',
            id='download-button',
            style={
                'marginBottom': '10px',
                'padding': '10px 20px',
                'backgroundColor': '#225A3E',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer'
            }
        ),
        dcc.Download(id='download-dataframe-csv'),
        html.Div([
            dash_table.DataTable(
                id='data-table',
                style_table={
                    'overflowX': 'auto',
                    'minWidth': '100%',
                    'maxHeight': '800px',  # 固定表高度
                    'overflowY': 'auto'    # 允許垂直滾動
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'minWidth': '100px',    # 最小列寬
                    'maxWidth': '180px',    # 最大列寬
                    'whiteSpace': 'normal', # 允許文字換行
                    'height': 'auto'
                },
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold',
                    'border': '1px solid #ddd'
                },
                style_data={
                    'border': '1px solid #ddd'
                },
                page_size=100  # 每頁顯示的行數
            )
        ], style={
            'margin': '0 auto',
            'maxWidth': '100%',
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '5px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        })
    ], style={
        'clear': 'both',
        'padding': '20px',
        'marginTop': '18px'
    }),

    # 添加 Footer
    html.Footer([
        html.Div([
            html.P('© 社群數據分析儀錶板 | 開發 : Rex Li | 版本 1.3.1', style={'margin': '0'}),
            html.P('聯絡電話 : 0916-800633', style={'margin': '5px 0'}),
            html.P([
                '聯絡資訊：',
                html.A('rexli01010629@email.com', 
                      href='mailto:rexli01010629@email.com',
                      style={
                          'color': '#fbad3c',
                          'textDecoration': 'none',
                          'marginLeft': '5px'
                      })
            ], style={'margin': '0'})
        ], style={
            'textAlign': 'center',
            'padding': '20px 0'
        })
    ], style={
        'backgroundColor': '#225A3E',
        'color': '#f1f1f1',
        'marginTop': '30px',
        'width': '100%',
        'bottom': '0',
        'fontSize': '14px'
    })
])  # app.layout 的結束括號

# 更新工作表選項
@app.callback(
    Output('sheet-dropdown', 'options'),
    Input('platform-dropdown', 'value')
)
def update_sheet_options(platform):
    if platform == 'FB':
        return [{'label': sheet, 'value': sheet} for sheet in fb_data.keys()]
    else:
        return [{'label': sheet, 'value': sheet} for sheet in ig_data.keys()]

# 修改數據比對區域的顯示方式
@app.callback(
    Output('comparison-section', 'style'),
    [Input('platform-dropdown', 'value'),
     Input('sheet-dropdown', 'value')]
)
def toggle_comparison_section(platform, sheet):
    if platform == 'FB' and sheet in ['貼文', '影片', '限動']:
        return {'display': 'block'}
    elif platform == 'IG' and sheet in ['圖文', '限時動態']:
        return {'display': 'block', 'marginTop': '20px'}
    return {'display': 'none'}

# 修改數據比對區域的內容
@app.callback(
    [Output('x-axis-dropdown', 'style'),
     Output('x-axis-dropdown', 'value'),
     Output('x-axis-dropdown', 'options'),
     Output('y-axis-dropdown', 'options'),
     Output('y-axis-dropdown', 'value'),
     Output('second-x-axis-dropdown', 'style'),
     Output('second-x-axis-dropdown', 'options'),
     Output('second-x-axis-dropdown', 'value'),
     Output('second-y-axis-dropdown', 'style'),
     Output('second-y-axis-dropdown', 'options'),
     Output('second-y-axis-dropdown', 'value')],
    [Input('platform-dropdown', 'value'),
     Input('sheet-dropdown', 'value')]
)
def update_comparison_options(platform, sheet):
    # 默認返回值保持不變
    default_return = (
        {'display': 'none'},  # x-axis style
        None,                 # x-axis value
        [],                  # x-axis options
        [],                  # y-axis options
        None,                # y-axis value
        {'display': 'none'}, # second-x-axis style
        [],                  # second-x-axis options
        None,                # second-x-axis value
        {'display': 'none'}, # second-y-axis style
        [],                  # second-y-axis options
        None                 # second-y-axis value
    )

    if not platform or not sheet:
        return default_return

    if platform == 'IG':
        if sheet == '圖文':
            # IG圖文的選項保持不變
            first_x_options = [
                {'label': '發布小時', 'value': '發布小時'},
                {'label': '分類', 'value': '分類'}
            ]
            first_y_options = [
                {'label': '觸及數量', 'value': '觸及數量'},
                {'label': '按讚數量', 'value': '按讚數量'},
                {'label': '分享數量', 'value': '分享數量'},
                {'label': '留言數量', 'value': '留言數量'},
                {'label': '珍藏次數', 'value': '珍藏次數'}
            ]
            return (
                {'display': 'block'}, 
                '發布小時',
                first_x_options,
                first_y_options,
                '觸及數量',
                {'display': 'none'},
                [],
                None,
                {'display': 'none'},
                [],
                None
            )
        elif sheet == '限時動態':
            # IG 限時動態的選項
            first_x_options = [
                {'label': '張貼時間', 'value': '張貼時間'},
                {'label': '觸及數量', 'value': '觸及數量'}
            ]
            first_y_options = [
                {'label': '引導率', 'value': '引導率'},
                {'label': '觸及數量', 'value': '觸及數量'},
                {'label': '按讚數量', 'value': '按讚數量'},
                {'label': '分享率別', 'value': '分享率別'},
            ]
            second_x_options = [
                {'label': '張貼時間', 'value': '張貼時間'}
            ]
            second_y_options = [
                {'label': '觸及數量', 'value': '觸及數量'},
                {'label': '按讚數量', 'value': '按讚數量'},
                {'label': '分享率別', 'value': '分享率別'},
                {'label': '引導率', 'value': '引導率'}
            ]
            return (
                {'display': 'block'}, 
                '張貼時間',
                first_x_options,
                first_y_options,
                '引導率',
                {'display': 'block'},
                second_x_options,
                '張貼時間',
                {'display': 'block'},
                second_y_options,
                '按讚數量'
            )
    elif platform == 'FB':
        if sheet == '貼文':
            # FB貼文的選項
            first_x_options = [
                {'label': '發布日期', 'value': '發布日期'},
                {'label': '發布時間', 'value': '發布時間'},
                {'label': '類別', 'value': '類別'}
            ]
            first_y_options = [
                {'label': '觸及人數', 'value': '觸及人數'},
                {'label': '心情', 'value': '心情'},
                {'label': '留言', 'value': '留言'},
                {'label': '分享', 'value': '分享'},
                {'label': '總點擊次數', 'value': '總點擊次數'},
                {'label': '連結點擊次數', 'value': '連結點擊次數'}
            ]
            second_x_options = [
                {'label': '心情', 'value': '心情'},
                {'label': '發布時間', 'value': '發布時間'},
                {'label': '類別', 'value': '類別'}
            ]
            second_y_options = [
                {'label': '留言', 'value': '留言'},
                {'label': '分享', 'value': '分享'},
                {'label': '總點擊次數', 'value': '總點擊次數'},
                {'label': '連結點擊次數', 'value': '連結點擊次數'}
            ]
            return (
                {'display': 'block'}, 
                '發布日期',  # 預設X軸
                first_x_options,
                first_y_options,
                '留言',  # 預設Y軸
                {'display': 'block'},  # 顯示第二組選單
                second_x_options,
                '類別',  # 預設第二個X軸
                {'display': 'block'},
                second_y_options,
                '總點擊次數'  # 預設第二個Y軸
            )
        elif sheet == '影片':
            # FB影片的選項
            first_x_options = [{'label': '心情', 'value': '心情'}]
            first_y_options = [
                {'label': '3秒觀看數', 'value': '影片觀看 3 ��以上的次數'},
                {'label': '觸及人數', 'value': '觸及人數'},
                {'label': '留言', 'value': '留言'},
                {'label': '分享', 'value': '分享'}
            ]
            second_x_options = [{'label': '發布時間', 'value': '發布時間'}]
            return (
                {'display': 'block'},
                '心情',
                first_x_options,
                first_y_options,
                '影片觀看 3 秒以上的次數',
                {'display': 'block'},
                second_x_options,
                '發布時間',
                {'display': 'block'},
                first_y_options,
                '觸及人數'
            )
        elif sheet == '限動':
            # FB限動的選項
            first_x_options = [{'label': '發布時間', 'value': '發布時間'}]
            first_y_options = [
                {'label': '觸及人數', 'value': '觸及人數'},
                {'label': '讚數', 'value': '讚數'},
                {'label': '回覆數', 'value': '回覆數'},
                {'label': '分享數', 'value': '分享數'}
            ]
            second_x_options = [{'label': '無特殊交互事項', 'value': 'none'}]
            second_y_options = [{'label': '無特殊交互事項', 'value': 'none'}]
            return (
                {'display': 'block'},
                '發布時間',
                first_x_options,
                first_y_options,
                '觸及人數',
                {'display': 'block'},
                second_x_options,
                'none',
                {'display': 'block'},
                second_y_options,
                'none'
            )
    
    # 如果沒有匹配到任何條件，返回默認值
    return default_return

# 修改圖表顯示區域布局的回調函數
@app.callback(
    [Output('first-graph-container', 'style'),
     Output('second-graph-container', 'style')],
    [Input('platform-dropdown', 'value'),
     Input('sheet-dropdown', 'value')]
)
def update_graph_layout(platform, sheet):
    base_style = {
        'border': '1px solid #ddd',
        'borderRadius': '10px',
        'padding': '10px',
        'boxShadow': '2px 2px 5px rgba(0,0,0,0.1)',
    }
    
    # 第一個圖表的基本樣式
    first_style = {
        **base_style,
        'marginBottom': '20px',
        'backgroundColor': 'maroon',
        'backgroundImage': 'url("/assets/background.jpg")',
        'backgroundSize': 'cover',
        'backgroundPosition': 'center',
    }
    
    # 第二個圖表的基本樣式
    second_style = {
        **base_style,
        'backgroundColor': 'teal',
    }

    # 對於所有類型，包括限動，都顯示兩個圖表容器
    first_style['height'] = '41vh'
    first_style['display'] = 'block'
    second_style['height'] = '41vh'
    second_style['display'] = 'block'
    
    return first_style, second_style

# 修改圓餅圖的回調
@app.callback(
    Output('category-pie-chart', 'figure'),
    [Input('platform-dropdown', 'value'),
     Input('sheet-dropdown', 'value')]
)
def update_pie_chart(platform, sheet):
    if not sheet:
        return {}
    
    # 創建空白圖表（用於影片和限動）
    blank_fig = {
        'data': [],
        'layout': {
            'annotations': [{
                'text': '影片、限動沒有類別',
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {
                    'size': 24,
                    'color': '#666'
                },
                'x': 0.5,
                'y': 0.5,
                'xanchor': 'center',
                'yanchor': 'middle'
            }],
            'height': 300,
            'margin': dict(t=40, b=20, l=20, r=20),
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    # 對於影片和限動數據，返回提示文字
    if sheet in ['影片', '限動', '限時動態']:
        return blank_fig
    
    try:
        # 根據平台選擇正確的數據和工作表名稱
        if platform == 'FB' and sheet == '貼文':
            df = fb_data[sheet]  # FB使用原始工作表名稱
            category_counts = df['類別'].value_counts()
        elif platform == 'IG' and sheet == '圖文':
            df = ig_data[sheet]  # 直接使用 sheet 而不是 sheet_name
            category_counts = df['分類'].value_counts()
        
        # 只顯示前10名，其餘歸類為"其他"
        top_10 = category_counts.head(10)
        if len(category_counts) > 10:
            others = pd.Series({'其他': category_counts[10:].sum()})
            category_counts = pd.concat([top_10, others])
        
        fig = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title='各類別所占比例（前十名）'
        )
        fig.update_layout(
            showlegend=True,
            margin=dict(t=40, b=20, l=20, r=20),
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title={
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='%{label}<br>數量: %{value}<br>比例: %{percent}'
        )
        return fig
    except KeyError:
        # 如果找不到工作表，返回空白圖表
        return blank_fig

# 修改原有的更新圖表回調函數 - 合併所有圖表更新
@app.callback(
    [Output('share-rate-graph', 'figure'),
     Output('reach-graph', 'figure'),
     Output('data-table', 'data'),
     Output('data-table', 'columns'),
     Output('data-title', 'children')],
    [Input('platform-dropdown', 'value'),
     Input('sheet-dropdown', 'value'),
     Input('x-axis-dropdown', 'value'),
     Input('y-axis-dropdown', 'value'),
     Input('second-x-axis-dropdown', 'value'),
     Input('second-y-axis-dropdown', 'value')]
)
def update_graphs_and_table(platform, sheet, x_axis, y_axis, second_x_axis, second_y_axis):
    try:
        if not sheet or y_axis is None:
            return dash.no_update, dash.no_update, [], [], ''
        
        df = fb_data[sheet] if platform == 'FB' else ig_data[sheet]
        df = df.copy()
        
        platform_name = 'Facebook' if platform == 'FB' else 'Instagram'
        title = f'{platform_name} - {sheet} 所有數據'
        
        share_fig = go.Figure()
        reach_fig = go.Figure()
        
        # Facebook 貼文的圖表邏輯
        if platform == 'FB' and sheet == '貼文':
            if x_axis == '發布日期':
                share_fig = px.line(df, 
                                  x=x_axis, 
                                  y=y_axis,
                                  title=f'{y_axis}趨勢圖')
            elif x_axis == '發布時間':
                share_fig = px.histogram(df, 
                                       x=x_axis, 
                                       y=y_axis,
                                       color='發布時間',
                                       title=f'{x_axis}與{y_axis}分布')
            elif x_axis == '類別':
                # 創建類別簡稱
                df['類別_簡稱'] = df['類別'].apply(lambda x: str(x)[:5])
                share_fig = px.bar(df, 
                                 x='類別_簡稱', 
                                 y=y_axis,
                                 color='類別_簡稱',
                                 title=f'{y_axis}的類別分布')
            
            # 第二張圖的邏輯
            if second_x_axis == '心情':
                reach_fig = px.scatter(df, 
                                     x=second_x_axis, 
                                     y=second_y_axis,
                                     color_discrete_sequence=px.colors.qualitative.Alphabet_r,
                                     title=f'{second_x_axis}與{second_y_axis}關係')
            elif second_x_axis == '發布時間':
                reach_fig = px.density_heatmap(df, 
                                             x=second_x_axis, 
                                             y=second_y_axis,
                                             color_continuous_scale=px.colors.sequential.Inferno_r,
                                             title=f'{second_x_axis}與{second_y_axis}分布熱力圖')
            elif second_x_axis == '類別':
                # 創建類別簡稱
                df['類別_簡稱'] = df['類別'].apply(lambda x: str(x)[:5])
                reach_fig = px.box(df, 
                                 x='類別_簡稱', 
                                 y=second_y_axis,
                                 color='類別_簡稱',
                                 title=f'{second_y_axis}的類別分布')

        # Facebook 影片的圖表邏輯
        elif platform == 'FB' and sheet == '影片':
            # 第一張圖：心情散點圖
            share_fig = px.scatter(df, x='心情', y=y_axis,
                                 title=f'心情與{y_axis}關係圖')
            
            # 添加對角線
            x_range = [df['心情'].min(), df['心情'].max()]
            share_fig.add_trace(
                go.Scatter(x=x_range, y=x_range,
                          mode='lines',
                          name='對角線',
                          line=dict(color='red', dash='dash'))
            )
            
            # 第二張圖：發布時間直方圖
            reach_fig = px.histogram(df,
                                   x='發布時間',
                                   y=second_y_axis,
                                   color='發布時間',
                                   color_discrete_sequence=px.colors.qualitative.Set2,
                                   title=f'發布時間與{second_y_axis}分布')
            
        # Facebook 限動的圖表邏輯
        elif platform == 'FB' and sheet == '限動':
            # 第一張圖：發布時間直方圖
            share_fig = px.histogram(df,
                                   x='發布時間',
                                   y=y_axis,
                                   color='發布時間',
                                   title=f'發布時間與{y_axis}分布')
            
            # 第二張圖：顯示提示訊息（保持為獨立圖表）
            reach_fig = go.Figure()
            reach_fig.add_annotation(
                text="無特殊交互事項",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=24, color='#666')
            )
            reach_fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=50, r=20, t=40, b=30),
                height=400
            )

        # Instagram 圖文的圖表邏輯
        if platform == 'IG' and sheet == '圖文':
            if x_axis == '發布小時':
                share_fig = px.bar(df, 
                                 x=x_axis, 
                                 y=y_axis,
                                 title=f'{x_axis}與{y_axis}分布')
            elif x_axis == '分類':
                # 創建類別簡稱
                df['分類_簡稱'] = df['分類'].apply(lambda x: str(x)[:5])
                share_fig = px.box(df, 
                                 x='分類_簡稱', 
                                 y=y_axis,
                                 color='分類_簡稱',
                                 title=f'{y_axis}的分類分布')

            # 第二張圖保持空白或顯示其他資訊
            reach_fig = go.Figure()
            reach_fig.add_annotation(
                text="沒有需要交互的項目",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=24, color='#666')
            )

        # Instagram 限時動態的圖表邏輯
        elif platform == 'IG' and sheet == '限時動態':
            # 第一張圖
            if x_axis == '張貼時間':
                share_fig = px.bar(df,
                                 x=x_axis,
                                 y=y_axis,
                                 color='張貼時間',
                                 color_discrete_sequence=px.colors.qualitative.Alphabet_r,
                                 title=f'{x_axis}與{y_axis}分布')
            elif x_axis == '觸及數量':
                share_fig = px.scatter(df,
                                     x=x_axis,
                                     y=y_axis,
                                     color_discrete_sequence = px.colors.qualitative.Alphabet_r,
                                     title=f'{x_axis}與{y_axis}關係')
            
            # 第二張圖
            reach_fig = px.density_heatmap(df,
                                         x=second_x_axis,
                                         y=second_y_axis,
                                         color_continuous_scale=px.colors.sequential.Inferno_r,
                                         title=f'{second_x_axis}與{second_y_axis}分布熱力圖')

        # Facebook 影片的圖表邏輯部分
        elif platform == 'FB' and sheet == '影片':
            if x_axis == '心情':
                share_fig = px.scatter(df, 
                                     x=x_axis, 
                                     y=y_axis,
                                     title=f'{x_axis}與{y_axis}關係')
                
                # 根據Y軸選擇設置不同的範圍
                x_range = [0, 600]  # X軸範圍固定
                if y_axis in ['留言', '分享']:
                    y_range = [0, 600]  # 留言和分享的Y軸範圍
                else:
                    y_range = [0, 40000]  # 3秒觀看數和觸及人數的Y軸範圍
                
                # 添加對角線
                share_fig.add_trace(
                    go.Scatter(x=x_range, 
                              y=y_range,
                              mode='lines',
                              name='對角線',
                              line=dict(color='red', dash='dash'))
                )
                share_fig.update_layout(
                    xaxis_range=x_range,
                    yaxis_range=y_range
                )
            
            # 第二張圖的邏輯保持不變
            reach_fig = px.histogram(df,
                                   x=second_x_axis,
                                   y=second_y_axis,
                                   color='發布時間',
                                   color_discrete_sequence=px.colors.qualitative.Set2,
                                   title=f'發布時間與{second_y_axis}分布')

        # 更新所有圖表的布局
        for fig in [share_fig, reach_fig]:
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=50, r=20, t=40, b=30),
                title={
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )
        
        return share_fig, reach_fig, df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], title
        
    except Exception as e:
        print(f"Error in update_graphs_and_table: {str(e)}")
        error_fig = go.Figure()
        error_fig.add_annotation(
            text=f"圖表生成錯誤: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return error_fig, error_fig, [], [], "錯誤"

# 添加下載功能的回調
@app.callback(
    Output('download-dataframe-csv', 'data'),
    Input('download-button', 'n_clicks'),
    [State('platform-dropdown', 'value'),
     State('sheet-dropdown', 'value')],
    prevent_initial_call=True
)
def download_data(n_clicks, platform, sheet):
    if n_clicks is None:
        return dash.no_update
    
    try:
        df = fb_data[sheet] if platform == 'FB' else ig_data[sheet]
        return dcc.send_data_frame(df.to_csv, f"{platform}_{sheet}_data.csv", encoding='utf-8-sig', index=False)
    except Exception as e:
        print(f"下載錯誤: {str(e)}")
        return dash.no_update

# 添加全局錯誤處理啟動
app.config.suppress_callback_exceptions = True

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False)
# dev_tools_ui=False