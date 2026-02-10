import numpy as np
import pandas as pd
import os


class AbstractProcessor:

    def __init__(self, config):
        self.config = config
        if config['forms']['col_names']:
            self.columns = config['forms']['col_names'] + ['status']
        else:
            self.columns = list(pd.read_excel(self.config['forms']['path'], sheet_name=0, skiprows=self.skip_rows).columns) + ['status']
        self.skip_rows = self.config['forms']['skip']

    def synchronize_forms(self):
        forms = pd.read_excel(self.config['forms']['path'], sheet_name=0, skiprows=self.skip_rows, names=self.config['forms']['col_names'])
        forms = forms[forms.typ != self.config['forms']['bierny']]
        if os.path.exists(self.config['assessed']['path']):
            csv = pd.read_csv(self.config['assessed']['path'])
        else:
            csv = forms
            csv['status'] = [self.config['assessed']['status']['todo']] * len(csv)

        if len(forms) > len(csv):
            temp = forms.iloc[len(csv):].copy()
            temp['status'] = [self.config['assessed']['status']['todo']] * len(temp)
            csv = pd.concat((csv, temp))

        self.data = csv

    def get_abstract(self, index: int) -> str:
        row = self.data.iloc[index]
        abstract = ""
        for type in self.config['forms']['abstract_types']:
            cols = [e for e in self.columns if type == e.split('_')[0]]
            data_here = row[cols]
            if not np.any(data_here.isna()):
                for c in cols:
                    abstract += c.split('_')[1].title() + '\n'
                    abstract += data_here[c] + '\n\n'
        return abstract

    def get_abstract_status(self, index: int) -> str:
        return self.data.iat[index, -1]

    def set_abstract_status(self, index: int, status: str):
        self.data.iat[index, -1] = self.config['assessed']['status'][status]

    def n_abstracts(self) -> int:
        return len(self.data)

    def any_to_assess(self):
        return np.any(self.data[self.columns[-1]] == self.config['assessed']['status']['todo']) or np.any(self.data[self.columns[-1]] == self.config['assessed']['status']['fix'])

    def save_synced(self):
        self.data.to_csv(self.config['assessed']['path'])

    def export_abstract(self, index: int):
        row = self.data.iloc[index]
        abstract = f"Autor: {row['imię']} {row['nazwisko']}, email: {row['email']}\n\n"
        abstract += self.get_abstract(index)
        with open(os.path.join(self.config['assessed']['abstracts_dir'], f"{row['imię'].lower()}_{row['nazwisko'].lower()}.txt"), 'w') as f:
            f.write(abstract)

    def load_from_txt(self, index: int) -> str:
        row = self.data.iloc[index]
        with open(os.path.join(self.config['assessed']['abstracts_dir'], f"{row['imię'].lower()}_{row['nazwisko'].lower()}.txt"), 'r') as f:
            return f.read()

    def get_email(self, index: int) -> str:
        return self.data.iat[index, self.columns.index('email')]


    def render_abstract(self, index: int):
        pass
