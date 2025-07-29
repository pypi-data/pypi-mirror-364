from lifelines import CoxPHFitter

def fit_cox(df, duration_col, event_col):
    model = CoxPHFitter()
    model.fit(df, duration_col=duration_col, event_col=event_col)
    return model
