import re

import pandas as pd




class rtm():
    def __init__(self):
        self.total_case=None
        self.total_case_pass=None
        self.total_case_fail=None

        self.total_req=None
        self.total_req_pass=None
        self.total_req_fail=None
        self.total_req_PF=None

        self.total_module_num=None
        self.req_module_summary=None
        self.case_module_summary = None

        self.rtm_raw_df=None
        self.rtm_init_df=None
        self.module_num=None
        self.req_id_col_name='ID'
        self.req_module_col_name='module'
        self.req_result_col_name='result'
        self.case_id_col_name = 'ID.1'
        self.case_module_col_name = 'module.1'
        self.case_result_col_name = 'result.1'

    def read_excel(self,io,*args,**kwargs):
        try:
            # 使用 *args 和 **kwargs 调用 pd.read_excel
            self.rtm_raw_df = pd.read_excel(io,*args, **kwargs)
            self.rtm_init_df=self.rtm_raw_df.loc[:,[self.req_module_col_name,self.req_id_col_name,self.req_result_col_name,
                                                    self.case_module_col_name,self.case_id_col_name,self.case_result_col_name]]
            # self.rtm_init_df['req_mouule_id']=self.rtm_init_df[self.req_module_col_name]+self.rtm_init_df[self.req_id_col_name]

            self.rtm_init_df.insert(self.rtm_init_df.columns.get_loc(self.req_id_col_name) + 1, 'req_module_id',
                                    self.rtm_init_df[self.req_module_col_name] + self.rtm_init_df[self.req_id_col_name])
            self.rtm_init_df.insert(self.rtm_init_df.columns.get_loc(self.case_id_col_name) + 1, 'case_module_id',
                                    self.rtm_init_df[self.case_module_col_name] + self.rtm_init_df[self.case_id_col_name])

            self.rtm_init_df.to_excel('./out.xlsx')
        except Exception as e:
            print(f"Error reading Excel file: {e}")



    def get_module(self):
        req_module=self.rtm_init_df[self.req_module_col_name].dropna().drop_duplicates().reset_index(drop=True)
        case_module = self.rtm_init_df[self.case_module_col_name].dropna().drop_duplicates().reset_index(drop=True)
        num1 = req_module.size
        num2 = case_module.size
        if num1==num2:
            self.total_module_num=num1
            self.req_module_summary=req_module.to_frame()
            self.case_module_summary = case_module.to_frame()
            # self.req_module_summary['module_short']=re.search(r'/\d\d\d\d_(\w+)$',self.req_module_summary['module']).group(1)
            self.req_module_summary['module_short'] = self.req_module_summary[self.req_module_col_name].apply(
                lambda x: re.search(r'\d{4}_(\w+)$', x).group(0) if re.search(r'\d{4}_(\w+)$', x) else None
            )
            self.case_module_summary['module_short'] = self.case_module_summary[self.case_module_col_name].apply(
                lambda x: re.search(r'\d{4}_(\w+)$', x).group(0) if re.search(r'\d{4}_(\w+)$', x) else None
            )

            print(self.req_module_summary)
            print(self.case_module_summary)


    def data_analysis(self):
        self.total_case=self.rtm_init_df['case_module_id'].nunique()
        self.total_req = self.rtm_init_df['req_module_id'].nunique()
        self.get_module()





if __name__ == "__main__":
    rtm1=rtm()
    rtm1.read_excel(io='./rtm.xlsx',skipfooter=0)
    rtm1.data_analysis()

