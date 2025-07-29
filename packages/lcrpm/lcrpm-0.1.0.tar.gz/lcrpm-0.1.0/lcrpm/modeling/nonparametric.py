from lifelines import KaplanMeierFitter, NelsonAalenFitter

def fit_kaplan_meier(df, duration_col, event_col):
    kmf = KaplanMeierFitter()
    kmf.fit(df[duration_col], df[event_col])
    return kmf
