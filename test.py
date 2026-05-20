# testing for smoking status features 


df = pd.read_csv('KNHANES9.csv') 
cols = ['BS1_1', 'BS2_1', 'BS2_2', 'BS3_3', 'BS6_2', 'BS6_2_1', 'BS6_2_2', 'BS6_3', 'BS6_4', 'BS6_4_1', 'BS6_4_2']
# ^ these are the smoking features that will be used just for testing and seeing NaN value count 
for col in cols:
    if col in df.columns:
        print(f"{col}: {df.columns.get_loc(col)}")
    else:
        print(f"{col}: NOT FOUND")

df_subset = (df.iloc[:, [1,9,12,15,234, 303, 304, 520, 535, 496,
                          300, 301, 302, 305, 306, 307, 308, 309, 310, 311, 312]])
age_threshold = 50 
df_subset = df_subset[df_subset['age'] >= age_threshold]
print(df_subset.head(1))
