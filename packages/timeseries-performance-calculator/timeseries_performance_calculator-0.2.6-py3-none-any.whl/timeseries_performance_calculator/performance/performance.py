from functools import cached_property
from universal_timeseries_transformer import PricesMatrix
from timeseries_performance_calculator.tables.total import get_table_total_performance, get_dfs_tables_year
from timeseries_performance_calculator.tables.period_returns_table import get_table_period_returns
from timeseries_performance_calculator.tables.yearly_returns_table import get_table_yearly_returns
from timeseries_performance_calculator.tables.monthly_returns_table import get_table_monthly_returns


class Performance:
    def __init__(self, timeseries):
        self.timeseries = timeseries

    @cached_property
    def pm(self):
        return PricesMatrix(self.timeseries)
    
    @cached_property
    def prices(self):
        return self.pm.df

    @cached_property
    def returns(self):
        return self.pm.returns
    
    @cached_property
    def cumreturns(self):
        return self.pm.cumreturns
    
    @cached_property
    def total_performance(self):
        return get_table_total_performance(self.prices)
    
    @cached_property
    def period_returns(self):
        return get_table_period_returns(self.prices)
    
    @cached_property
    def yearly_returns(self):
        return get_table_yearly_returns(self.prices)
    
    @cached_property
    def monthly_returns(self):
        return get_table_monthly_returns(self.prices)
    
    @cached_property
    def dfs_tables_year(self):
        return get_dfs_tables_year(self.prices)
    