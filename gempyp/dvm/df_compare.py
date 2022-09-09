import sys
from telnetlib import STATUS
import traceback
from numpy import sort
import pandas as pd



def df_compare(df_1, df_2, key,reporter):
    try:
        #print(df_1)
        #print('======================================================')
        #print(df_2)
        #print('======================================================')
        # print(df_1.eq(df_2))
        #df_1['key'] = df_1[key].agg('-'.join, axis=1)
        df_1['key'] = df_1[key].apply(lambda row: '--'.join(row.values.astype(str)), axis=1)
        df_2['key'] = df_2[key].apply(lambda row: '--'.join(row.values.astype(str)), axis=1)
        df_1.set_index('key', inplace=True)
        df_2.set_index('key', inplace=True)
        df_1.drop(key, axis=1, inplace=True)
        df_2.drop(key, axis=1, inplace=True)
        src_key_values = df_1.index.values
        tgt_key_values = df_2.index.values
        headers = list(set(list(df_1.columns)) - set(key+['key']))
        common_keys = list(set(src_key_values) & set(tgt_key_values))
        keys_only_in_src = list(set(src_key_values) - set(tgt_key_values))
        keys_only_in_tgt = list(set(tgt_key_values) - set(src_key_values))
        #print(common_keys,keys_only_in_src, keys_only_in_tgt, list(headers))
        diff_list = []
        if common_keys:
            for key_val in common_keys:
                for field in headers:
                    src_val = df_1.loc[key_val,field]
                    tgt_val = df_2.loc[key_val,field]
                    if src_val != tgt_val:
                        # reporter.addrow({'key':key_val, 'column': field, 'src_value':src_val, 'tgt_value':tgt_val,
                        # 'ROF':'Value mismatch' if type(src_val)==type(tgt_val) else 'Data type diff' })
                        reporter.addRow("keys","description is working",STATUS.PASS)
                        reporter.addMisc("keys",key_val)
                        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                        print("Addrow is working")
        if diff_list:
            diff_df = pd.DataFrame(diff_list,
                            columns=['key','column','src_value', 'tgt_value', 'ROF'])
            diff_df.set_index('key', inplace=True)
            return {'Keys': key,'Common_keys': sorted(common_keys), 'Keys_only_in_source': sorted(keys_only_in_src),
            'Keys_only_in_target': sorted(keys_only_in_tgt),'Difference_df': diff_df.sort_index(axis=0).to_json(orient="split")}
        else:
            return -1
    except Exception:
        traceback.print_exc()


# if __name__ == '__main__':
#     array_1 = [[1,'LeBron',3,'0'],
#                         [2,'Kobe',5,'1'],
#                         [3,'Michael',6,'2'],
#                         [4,'Larr','5','3'],
#                         [5,'Magic',5,'4'],
#                         [6,'Tim',4,'5'],
#                         [7,'test1',9,'6']]
#     df_1 = pd.DataFrame(array_1, 
#                         columns=['id1','Player','Rings','id2'])
#     # Data from friend
#     array_2 = [[1,'LeBron',3,'1'],
#                         [2,'Kobe',3,'9'],
#                         [3,'Michael!',6,'2'],
#                         [4,'Larry',5,'3'],
#                         [5,'Magicl',5,'4'],
#                         [6,'Tim',4,'5'],
#                         [10,'test2',0,'6']]
#     df_2 = pd.DataFrame(array_2, 
#                         columns=['id1','Player','Rings','id2'])
#     res = df_compare(df_1, df_2, ['id1', 'id2'])
#     print(res)
#     print(res['Difference_df'])
