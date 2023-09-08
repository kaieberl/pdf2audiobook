# check that labels do not contain \r or are empty
import pandas as pd

if __name__ == '__main__':
    dataset_list = ['Alex-001-features_.csv', 'cryp-001-features_.csv', 'ebm-001-features_.csv', 'Neua-001-features_.csv', 'Neur-001-features_.csv', 'SMS-001-features_.csv']
    for dataset in dataset_list:
        df = pd.read_csv(dataset)
        print(df['label'].unique())
        print(df['label'].value_counts())
        print(df['label'].isnull().sum())
        print(df['label'].str.contains('\r').sum())