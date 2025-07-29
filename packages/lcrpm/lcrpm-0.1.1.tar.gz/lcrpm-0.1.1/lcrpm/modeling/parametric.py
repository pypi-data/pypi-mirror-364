from lifelines import WeibullFitter, LogLogisticFitter

def fit_weibull(df, duration_col, event_col):
    model = WeibullFitter()
    model.fit(df[duration_col], df[event_col])
    return model
