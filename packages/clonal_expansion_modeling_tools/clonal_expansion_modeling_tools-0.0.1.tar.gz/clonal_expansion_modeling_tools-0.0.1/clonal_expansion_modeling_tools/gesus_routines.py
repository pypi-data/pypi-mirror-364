import pandas as pd
import numpy as np
import datetime

path_to_new_data = 'D:\\GESUS_followup\\Baseline to follow-upv8_dataprep_4.xlsx'
path_to_data_v5 = 'D:\\GESUS_followup\\Baseline to follow-upv5_anomyseret.xlsx'
path_to_cleaned_dataframe_pre_diagnosis = 'D:\\GESUS_followup\\merged_jak2_dataframe_all_67_pre_diagnosis.pkl'

def load_cleaned_dataframe_pre_diagnosis(path = path_to_cleaned_dataframe_pre_diagnosis):
    return pd.read_pickle(path)

def load_fake_data(path = 'data/fake_data_longer_followup.pkl'):
    print('WARNING: this data is fake')
    try:
        return pd.read_pickle(path)
    except FileNotFoundError:
        return pd.read_pickle('../'+path)

def fix_f_date(df):
    df['f_date'] = pd.to_datetime(df['f_date'], format='%d-%m-%Y')
    df1 = df.groupby(level=0)['f_date'].ffill()
    df.drop('f_date', axis=1, inplace=True)
    df = df.join(df1)
    return df


def fix_fremmoede_dato(df):
    # find all the indices where fremmoede_dato_dk is already a datetime
    idx = df['fremmoede_dato_dk'].apply(lambda x: type(x) != datetime.datetime)
    df.loc[idx, 'fremmoede_dato_dk'] = pd.to_datetime(
        df.loc[idx, 'fremmoede_dato_dk'], format='%d-%m-%Y')
    df['fremmoede_dato_dk'] = pd.to_datetime(df['fremmoede_dato_dk'])
    return df


def compute_age(df):
    df['age'] = df['fremmoede_dato_dk'] - df['f_date']
    return df


def trim(df):
    df.drop(columns=['vaf_baseline', 'vaf_followup',
            'obstid_t_diag'], inplace=True, errors='ignore')
    # this subject's records are corrupted (blank rows -> nonunique indices and not much information)
    # df.drop(index=46, inplace=True, errors='ignore')
    # df.drop(index=(59, 2), inplace=True, errors='ignore')
    df.dropna(subset='stat', inplace=True)
    return df


def floaterizer(foo):
    return np.array([x.right if type(x) == pd.Interval else x for x in foo], dtype=float)


def convert_interval_columns(df):
    # define which columns include ranges such as "<0.1"
    columns_with_intervals = ['baso', 'eosino', 'hscrp']

    # convert ranges to pandas Interval types
    for row in df.itertuples():
        for column in columns_with_intervals:
            try:
                old_val = getattr(row, column)
                if type(old_val) is str and old_val[0] == '<':
                    new_val = pd.Interval(
                        0, float(old_val[1:].replace(',', '.')))
                else:
                    new_val = old_val
                df.at[row.Index, column] = new_val
            except AttributeError:
                pass

    # for the columns with intervals, add a dummy column with a stand-in float value for convenience
    for colname in columns_with_intervals:
        newcolname = colname+'_float'
        df[newcolname] = floaterizer(df[colname])
    return df


def convert_percentage_columns(df):
    # define which columns should be converted to percentages (of total leukocytes)
    percentage_columns = ['neutro', 'baso', 'eosino', 'mono', 'lymfo']
    for colname in percentage_columns:
        newcolname = colname+'_pct'
        df[newcolname] = floaterizer(df[colname])/df['t_leu']
    df['reticulo_pct'] = 1e-3 * floaterizer(df['reticulo'])/df['ery']
    return df


def compute_nlr(df):
    # compute the neutrophil-to-lymphocyte ratio
    df['nlr'] = df['neutro'] / df['lymfo']
    return df


def prepare_dataframe(path_to_data, trim_fn = trim, version='v8'):
    if version=='v5':
        return prepare_dataframe_v5(path_to_data)
    df = pd.read_excel(path_to_data, index_col=[0, 1])
    df = trim_fn(df)
    df = fix_f_date(df)
    df = fix_fremmoede_dato(df)
    df = compute_age(df)
    df = convert_interval_columns(df)
    df = convert_percentage_columns(df)
    df = compute_nlr(df)
    return df

# def select_pre_diagnosis(df):
#     df['pre_diagnosis'] = np.zeros(len(df), dtype=bool)

#     for id in df.index.get_level_values(0).unique():
#         if df.loc[(id, 0), 'diag']==1:
#             diag_date = df.loc[(id, 0), 'diag_date_dk']
#             if pd.isnull(diag_date):
#                 # we don't know the diagnosis date, so assume it was before the first followup
#                 df.loc[id, 'pre_diagnosis'] = False
#                 df.loc[(id, 0), 'pre_diagnosis'] = True
#             else:
#                 # the diagnosis date is present; compare this to visit dates to filter
#                 visits_before_diagnosis = (df.loc[id, 'fremmoede_dato_dk'] < diag_date)
#                 df.loc[id].loc[visits_before_diagnosis, 'pre_diagnosis'] = True
#         else:
#             df.loc[id, 'pre_diagnosis'] = True
#     return df[df['pre_diagnosis']]


def select_pre_diagnosis(df):
    df['pre_diagnosis'] = np.ones(len(df), dtype=bool)

    for id in df.index.get_level_values(0).unique():
        diag_date = df.loc[(id, 0), 'diag_dato']
        bdate = df.loc[(id,0),'bdate']
        if pd.isnull(diag_date):
            # there was no diagnosis made, so all measurements are pre diagnosis
            pass
        else:
            # the diagnosis date is present; compare this to visit dates to filter
            age_at_diagnosis = diag_date - bdate
            visits_before_diagnosis = (df.loc[(id), 'age'] < diag_date)
            df.loc[id].loc[visits_before_diagnosis, 'pre_diagnosis'] = True
    return df[df['pre_diagnosis']]


def extract_bl_to_fu_vaf(df):
    # this function creates a dataframe from all records that have at least one followup measurement
    # columns are 'baseline', 'followup', and 'dt'
    if 'vaf_baseline' in df.columns:
        vaf_bl_colname = 'vaf_baseline'
    elif 'vaf_sam' in df.columns:
        vaf_bl_colname = 'vaf_sam'
        vaf_followup_colname = 'vaf_sam'
    elif 'vaf' in df.columns:
        vaf_bl_colname = 'vaf'
        vaf_followup_colname = 'vaf'
    else:
        raise ValueError('cannot find proper VAF column')

    bl = df.xs(0, level=1)[vaf_bl_colname]
    
    if 'fremmoede_dato_dk' in df.columns:
        datecolname = 'fremmoede_dato_dk'
    elif 'date' in df.columns:
        datecolname = 'date'
    else:
        raise ValueError('cannot find proper date column')

    t = (df.xs(1, level=1)[datecolname] - df.xs(0, level=1)[datecolname]) / np.timedelta64(1, 'D')
    fu = df.xs(1, level=1)[vaf_followup_colname]
    try:
        stat = (df.xs(0, level=1)['stat']!='JAK2V617F_Nocytosis').astype(int)
    except KeyError:
        stat = np.zeros_like(bl)
    newdf = pd.DataFrame({'baseline':bl, 'followup':fu, 'dt':t, 'stat':stat})
    return newdf[~np.isnan(newdf['followup'])]


def prepare_dataframe_v5(path_to_data):
    """
    This function is preserved here for posterity.
    It is the function that builds the correct data frame from the excel file 'Baseline to follow-upv5_anomyseret.xlsx'
    """
    df = pd.read_excel(path_to_data, index_col=[0, 1], )

    # convert date columns to dates with specified format
    df['fremmoede_dato'] = pd.to_datetime(
        df['fremmoede_dato'], format='%Y%m%d')
    df['f_date'] = pd.to_datetime(df['f_date'], format='%d-%m-%Y')

    # need to fill the 'f_date' field for visit>0
    df1 = df.groupby(level=0)['f_date'].ffill()
    df.drop('f_date', axis=1, inplace=True)
    df = df.join(df1)

    # recompute  age field
    df['age'] = (df['fremmoede_dato'] - df['f_date']) / np.timedelta64(1, 'Y') # type: ignore

    # correct typos
    df.at[(10, 6), 'ery'] = 4.6
    df.at[(15, 1), 'ery'] = 4.2
    df.at[(24, 8), 'ery'] = 5.5

    df.at[(12, 8), 'baso'] = '<0.1'
    df.at[(12, 13), 'baso'] = '<0.1'
    df.at[(3, 8), 'baso'] = 0.1

    # define which columns should have numerical values
    numerical_columns = ['vaf_baseline', 'vaf_followup', 'vaf_sam', 'ery', 'reticulo', 't_leu',
                         'hct', 'hgb', 'mcv', 'trombo', 'neutro', 'baso', 'eosino', 'mono', 'lymfo', 'hscrp', 'ldh']

    # define which columns include ranges such as "<0.1"
    columns_with_intervals = ['baso', 'eosino', 'hscrp']

    # convert ranges to pandas Interval types
    for row in df.itertuples():
        for column in columns_with_intervals:
            try:
                old_val = getattr(row, column)
                if type(old_val) is str and old_val[0] == '<':
                    new_val = pd.Interval(
                        0, float(old_val[1:].replace(',', '.')))
                else:
                    new_val = old_val
                df.at[row.Index, column] = new_val
            except AttributeError:
                pass
    # for the columns with intervals, add a dummy column with a stand-in float value for convenience

    def floaterizer(foo):
        return np.array([x.right if type(x) == pd.Interval else x for x in foo])

    for colname in columns_with_intervals:
        newcolname = colname+'_float'
        df[newcolname] = floaterizer(df[colname])

    # define which columns should be converted to percentages (of total leukocytes)
    percentage_columns = ['neutro', 'baso', 'eosino', 'mono', 'lymfo']
    for colname in percentage_columns:
        newcolname = colname+'_pct'
        df[newcolname] = floaterizer(df[colname])/df['t_leu']
    df['reticulo_pct'] = 1e-3 * floaterizer(df['reticulo'])/df['ery']

    # compute the neutrophil-to-lymphocyte ratio
    df['nlr'] = df['neutro'] / df['lymfo']
    return df


def get_tdata_ydata(df, subject_id):
    dfsubset = df.loc[(subject_id, slice(0, None)), ...]
    if len(dfsubset) == 0:
        raise ValueError('no followup data')
    if 'fremmoede_dato' in dfsubset.columns:
        tcol = dfsubset['fremmoede_dato']
    elif 'fremmoede_dato_dk' in dfsubset.columns:
        tcol = dfsubset['fremmoede_dato_dk']
    elif 'age' in dfsubset.columns:
        tcol = dfsubset['age']
    else:
        raise ValueError('no time column found')
    
    if 'vaf_sam' in dfsubset.columns:
        ycol = dfsubset['vaf_sam']
    elif 'vaf' in dfsubset.columns:
        ycol = dfsubset['vaf']
    tdata = ((tcol - tcol.iloc[0])/np.timedelta64(1, 'D')).to_numpy()
    ydata = (ycol/100).to_numpy() # type: ignore
    # remove NANs
    good_idx = (~np.isnan(tdata))*(~np.isnan(ydata))
    return tdata[good_idx], ydata[good_idx]


"""
FROM MKL'S CHIP MANUSCRIPT

normal range as defined by the regional laboratory reference values and sex: hemoglobin concentration >10.5mmol/L (male) or  >9.5mmol/L (female), hematocrit >0.50 (male) or  >0.46 (female), erythrocytes >5.7x1012/L (male) or  >5.2x1012/L (female), thrombocytes >390x109 /L, leukocytes >8.8x109/L, neutrophils >7.0x109/L, monocytes >0.7x109/L, eosinophils >0.5x109/L, basophils >0.1x109/L,  and lymphocytes >3.5x109/L. 
The neutrophil-to-lymphocyte ratio (NLR) was calculated as a proxy measure of chronic inflammation and used as NLR ≤1.9 vs. NLR >2 (30).

"""



normal_ranges = {
    'M': {
        'ery': (4, 5.9),
        'reticulo_pct': (0.005, 0.025),
        'hct': (.41, .50),
        'hgb': (8.7, 11.2),
        'mcv': (80, 100),
        'trombo': (150, 450),
        't_leu': (4.5, 11),
        'neutro': (2.5, 7),
        'baso_float': (0, 0.3),
        'eosino_float': (0, 0.5),
        'mono': (0.2, 0.8),
        'lymfo': (1, 4.8),
        'hscrp_float': (0, 3),
        'ldh': (135, 280),
        'nlr': (2.5/4.8, 7)
    },
    'K': {
        'ery': (3.8, 5.2),
        'reticulo_pct': (0.005, 0.025),
        'hct': (.36, .48),
        'hgb': (7.4, 9.9),
        'mcv': (80, 100),
        'trombo': (150, 450),
        't_leu': (4.5, 11),
        'neutro': (2.5, 7),
        'baso_float': (0, 0.3),
        'eosino_float': (0, 0.5),
        'mono': (0.2, 0.8),
        'lymfo': (1, 4.8),
        'hscrp_float': (0, 3),
        'ldh': (135, 280),
        'nlr': (2.5/4.8, 7)
    }
}
proper_names = {
    'vaf_sam': 'Allele Burden (%)',
    'vaf_baseline': 'Allele Burden (%), baseline',
    'vaf_followup': 'Allele Burden (%), followup',
    'ery': 'Erythrocytes (10^12/L)',
    'reticulo_pct': 'Reticulocytes (fraction of RBC)',
    'hct': 'Hematocrit (fraction)',
    'hgb': 'Hemoglobin (mmol/L)',
    'mcv': 'Mean Corpuscular Volume (fL)',
    'trombo': 'Thrombocytes (10^9/L)',
    't_leu': 'Total WBC (10^9/L)',
    'neutro': 'Neutrophils (10^9/L)',
    'baso_float': 'Basophils (10^9/L)',
    'eosino_float': 'Eosinophils (10^9/L)',
    'mono': 'Monocytes (10^9/L)',
    'lymfo': 'Lymphocytes (10^9/L)',
    'hscrp_float': 'C-reactive protein (mg/L)',
    'ldh': 'Lactate dehydrogenase (IU/L)',
    'nlr': 'Neutrophil to Lymphocyte Ratio'
}

codes = {'DD471': 'Kronisk myeloproliferativt syndrom',
         'MPN': 'MPN',
         'DD474': 'Primær og sekundær myelofibrose',
         'DZ038D': 'Obs. pga mistanke om blodsygdom',
         'DD473': 'Essentiel trombocytæmi',
         'DD459': 'Polycythaemia vera',
         'DD474B': 'Sekundær myelofibrose efter polycytæmia vera',
         'DD471B': 'Myeloproliferativ sygdom UNS',
         'DZ038': 'Obs. pga mistanke om anden sygdom eller tilstand',
         '**DD459**': 'Polycythaemia vera',
         'DC911 ': 'Kronisk lymfatisk leukæmi af B-celle type (B-CLL)'}
codes_english = {'DD471': 'chronic myeloproliferative syndrome',
                 'MPN': 'MPN',
                 'DD474': 'primary and secondary myelofibrosis',
                 'DZ038D': 'observation due to suspected blood disease',
                 'DD473': 'essential trombocythemia',
                 'DD459': 'polycythaemia vera',
                 'DD474B': 'secondary myelofibrosis after polycythaemia vera',
                 'DD471B': 'myeloproliferative disease UNS',
                 'DZ038': 'observation due to susepcted other disease or condition',
                 '**DD459**': 'polycythaemia vera',
                 'DC911 ': 'Chronic lymphocytic leukemia of B-cell type (B-CLL)'}

VAF_lower_limit_of_detection = 0.0009