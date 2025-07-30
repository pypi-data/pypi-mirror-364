from collections import defaultdict
from datetime import datetime
from typing import List, Dict


class LedgerAnalyst:
    def __init__(
        self,
        transactions: List[Dict],
        accounts: List[str],
        *,
        income_parents=("Ingresos", "Incoming"),
        expense_parents=("Gastos", "Expenses"),
        asset_parents=("Activos", "Assets"),
        liability_parents=("Pasivos", "Liabilities"),
    ):
        self.transactions = transactions
        self.accounts = accounts
        self.income_parents = income_parents
        self.expense_parents = expense_parents
        self.asset_parents = asset_parents
        self.liability_parents = liability_parents

    def _is_under_parent(self, account: str, parents: tuple) -> bool:
        return any(
            account.startswith(parent + ":") or account == parent for parent in parents
        )

    def _normalize_date(self, date_str: str) -> str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date().isoformat()
        except ValueError:
            return datetime.strptime(date_str, "%Y/%m/%d").date().isoformat()

    def get_daily_incomes_expenses(self) -> List[Dict]:
        summary = defaultdict(lambda: {"incoming": 0.0, "expenses": 0.0})

        for tx in self.transactions:
            date = self._normalize_date(tx["date"])
            for entry in tx["accounts"]:
                account = entry["account"]
                amount = entry["amount"]
                if self._is_under_parent(account, self.income_parents):
                    summary[date]["incoming"] += abs(amount)
                elif self._is_under_parent(account, self.expense_parents):
                    summary[date]["expenses"] += abs(amount)

        return [{"date": date, **values} for date, values in sorted(summary.items())]

    def _group_by_account(self, parent_types: tuple) -> Dict[str, float]:
        grouped = defaultdict(float)
        for tx in self.transactions:
            for entry in tx["accounts"]:
                account = entry["account"]
                amount = entry["amount"]
                if self._is_under_parent(account, parent_types):
                    grouped[account] += abs(amount)
        return grouped

    def get_expenses_pie(self) -> List[Dict]:
        grouped = self._group_by_account(self.expense_parents)
        return [{"account": k, "amount": v} for k, v in grouped.items()]

    def get_incomes_pie(self) -> List[Dict]:
        grouped = self._group_by_account(self.income_parents)
        return [{"account": k, "amount": v} for k, v in grouped.items()]

    def get_assets_summary(self) -> List[Dict]:
        grouped = self._group_by_account(self.asset_parents)
        return [{"account": k, "amount": v} for k, v in grouped.items()]

    def get_liabilities_summary(self) -> List[Dict]:
        grouped = self._group_by_account(self.liability_parents)
        return [{"account": k, "amount": v} for k, v in grouped.items()]

    def get_balance_by_day(self) -> List[Dict]:
        """Retorna el balance diario acumulado: ingresos - gastos"""
        daily_data = self.get_daily_incomes_expenses()
        balance = 0
        result = []
        for entry in daily_data:
            balance += entry["incoming"] - entry["expenses"]
            result.append({**entry, "balance": balance})
        return result

    def get_accounts_used(self) -> List[str]:
        """Lista de todas las cuentas usadas en las transacciones (sin duplicados)"""
        used = set()
        for tx in self.transactions:
            for entry in tx["accounts"]:
                used.add(entry["account"])
        return sorted(list(used))

    def get_monthly_incomes_expenses(self) -> List[Dict]:
        """Retorna un resumen mensual de ingresos y gastos"""
        summary = defaultdict(lambda: {"incoming": 0.0, "expenses": 0.0})

        for tx in self.transactions:
            date = self._normalize_date(tx["date"])
            month = date[:7]  # YYYY-MM
            for entry in tx["accounts"]:
                account = entry["account"]
                amount = entry["amount"]
                if self._is_under_parent(account, self.income_parents):
                    summary[month]["incoming"] += abs(amount)
                elif self._is_under_parent(account, self.expense_parents):
                    summary[month]["expenses"] += abs(amount)

        return [{"month": month, **values} for month, values in sorted(summary.items())]

    def get_expense_trends_by_category(self) -> Dict[str, Dict[str, float]]:
        """Retorna un resumen de tendencias de gastos por categoría mensual"""
        trends = defaultdict(lambda: defaultdict(float))  # {categoria: {mes: monto}}

        for tx in self.transactions:
            date = self._normalize_date(tx["date"])
            month = date[:7]
            for entry in tx["accounts"]:
                account = entry["account"]
                if self._is_under_parent(account, self.expense_parents):
                    trends[account][month] += abs(entry["amount"])

        # Opcional: transformar a lista de dicts si lo usas en gráficos
        return {k: dict(v) for k, v in trends.items()}

    def get_cashflow_by_month(self) -> List[Dict]:
        summary = defaultdict(lambda: {"in": 0.0, "out": 0.0, "net": 0.0})

        for tx in self.transactions:
            date = self._normalize_date(tx["date"])
            month = date[:7]
            for entry in tx["accounts"]:
                account = entry["account"]
                amount = entry["amount"]
                if self._is_under_parent(account, self.income_parents):
                    summary[month]["in"] += abs(amount)
                elif self._is_under_parent(account, self.expense_parents):
                    summary[month]["out"] += abs(amount)

        for month in summary:
            summary[month]["net"] = summary[month]["in"] - summary[month]["out"]

        return [{"month": m, **v} for m, v in sorted(summary.items())]

    def get_average_expense_per_category(self) -> List[Dict]:
        """Calcula el promedio mensual de gastos por categoría"""
        totals = defaultdict(float)
        months = set()

        for tx in self.transactions:
            date = self._normalize_date(tx["date"])
            month = date[:7]
            months.add(month)
            for entry in tx["accounts"]:
                account = entry["account"]
                if self._is_under_parent(account, self.expense_parents):
                    totals[account] += abs(entry["amount"])

        num_months = len(months)
        return [
            {"account": acc, "monthly_average": total / num_months}
            for acc, total in totals.items()
        ]

    def detect_unusual_expenses(self, threshold: float = 1.5) -> List[Dict]:
        """Detecta gastos inusuales basados en tendencias mensuales"""
        trends = self.get_expense_trends_by_category()
        alerts = []

        for account, monthly_data in trends.items():
            values = list(monthly_data.values())
            if len(values) < 2:
                continue  # Necesitas al menos 2 meses para comparar
            avg = sum(values) / len(values)
            last_month = sorted(monthly_data.keys())[-1]
            if monthly_data[last_month] > avg * threshold:
                alerts.append(
                    {
                        "account": account,
                        "month": last_month,
                        "amount": monthly_data[last_month],
                        "average": avg,
                        "alert": "Gasto inusualmente alto",
                    }
                )

        return alerts
