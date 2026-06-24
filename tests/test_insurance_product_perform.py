import pytest
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


class TestInsuranceDataProcessing:

    def test_premium_column_exists(self):
        df = pd.DataFrame({"age": [25, 35], "premium": [1200.0, 1800.0], "claims": [0, 1]})
        assert "premium" in df.columns

    def test_negative_premiums_removed(self):
        df = pd.DataFrame({"premium": [1200, -50, 1800, 0]})
        df_clean = df[df["premium"] > 0]
        assert (df_clean["premium"] <= 0).sum() == 0

    def test_age_binning(self):
        ages = pd.Series([22, 35, 45, 60, 70])
        bins = pd.cut(ages, bins=[0, 30, 45, 60, 100], labels=["young", "mid", "senior", "elder"])
        assert bins[0] == "young"
        assert bins[4] == "elder"

    def test_claim_rate_calculation(self):
        df = pd.DataFrame({"claims": [0, 1, 0, 0, 1, 1]})
        rate = df["claims"].mean()
        assert abs(rate - 0.5) < 0.01

    def test_no_duplicate_policies(self):
        df = pd.DataFrame({"policy_id": [1, 2, 3, 2], "premium": [100, 200, 300, 200]})
        df_unique = df.drop_duplicates("policy_id")
        assert len(df_unique) == 3


class TestPerformanceAnalytics:

    def test_regression_r2_positive(self):
        np.random.seed(42)
        X = np.random.rand(200, 4)
        y = X[:, 0] * 5000 + X[:, 1] * 2000 + np.random.randn(200) * 100
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        r2 = r2_score(y_test, model.predict(X_test))
        assert r2 > 0

    def test_profit_loss_computation(self):
        premiums = np.array([1200, 1500, 900])
        claims = np.array([800, 2000, 0])
        profit = premiums - claims
        assert profit[0] > 0
        assert profit[1] < 0
