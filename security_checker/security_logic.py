"""
Модуль проверки безопасности облачной инфраструктуры
Вариант 32 - Контейнер безопасности облака
"""

import os
from datetime import datetime
from django.conf import settings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class SecurityChecker:
    def __init__(self):
        self.findings = []

    def run_full_check(self):
        self.findings = []

        # Тестовые данные
        buckets = [
            {"name": "customer-data", "public": True, "has_pii": True},
            {"name": "public-logs", "public": True, "has_pii": False},
            {"name": "private-backup", "public": False, "has_pii": True},
            {"name": "analytics-data", "public": True, "has_pii": True},
        ]

        users = [
            {"name": "admin", "rights": "full_access", "mfa_enabled": False},
            {"name": "developer", "rights": "read_only", "mfa_enabled": True},
            {"name": "service-account", "rights": "full_access", "mfa_enabled": False},
        ]

        services = [
            {"name": "Compute Engine", "status": "problem"},
            {"name": "Cloud Storage", "status": "ok"},
            {"name": "BigQuery", "status": "problem"},
        ]

        resources = [
            {"name": "backup-storage", "encrypted": False},
            {"name": "logs", "encrypted": False},
            {"name": "database", "encrypted": True},
            {"name": "user-data", "encrypted": False},
        ]

        # Проверка хранилищ
        for bucket in buckets:
            if bucket["public"] and bucket["has_pii"]:
                self.findings.append({
                    'resource': bucket['name'], 'type': 'storage',
                    'severity': 'CRITICAL',
                    'message': f"Хранилище {bucket['name']} публично и содержит ПД",
                    'remediation': 'Немедленно сделать хранилище приватным',
                    'responsible': 'consumer'
                })
            elif bucket["public"]:
                self.findings.append({
                    'resource': bucket['name'], 'type': 'storage',
                    'severity': 'WARNING',
                    'message': f"Хранилище {bucket['name']} публично доступно",
                    'remediation': 'Проверить необходимость публичного доступа',
                    'responsible': 'consumer'
                })

        # Проверка прав
        for user in users:
            if user["rights"] == "full_access":
                self.findings.append({
                    'resource': user['name'], 'type': 'iam',
                    'severity': 'CRITICAL',
                    'message': f"Пользователь {user['name']} имеет полные права",
                    'remediation': 'Применить принцип минимальных привилегий',
                    'responsible': 'consumer'
                })
            if not user.get("mfa_enabled", True):
                self.findings.append({
                    'resource': user['name'], 'type': 'iam',
                    'severity': 'CRITICAL',
                    'message': f"У пользователя {user['name']} отключена MFA",
                    'remediation': 'Включить многофакторную аутентификацию',
                    'responsible': 'consumer'
                })

        # Проверка SLA
        for service in services:
            if service["status"] != "ok":
                self.findings.append({
                    'resource': service['name'], 'type': 'service',
                    'severity': 'WARNING',
                    'message': f"Сервис {service['name']} работает с нарушениями SLA",
                    'remediation': 'Связаться с поддержкой провайдера',
                    'responsible': 'provider'
                })

        # Проверка шифрования
        for resource in resources:
            if not resource["encrypted"]:
                self.findings.append({
                    'resource': resource['name'], 'type': 'storage',
                    'severity': 'CRITICAL',
                    'message': f"Ресурс {resource['name']} не зашифрован",
                    'remediation': 'Включить шифрование данных',
                    'responsible': 'consumer'
                })

        return self.findings


def calculate_metrics(findings):
    critical = sum(1 for f in findings if f.get('severity') == 'CRITICAL')
    warning = sum(1 for f in findings if f.get('severity') == 'WARNING')
    provider = sum(1 for f in findings if f.get('responsible') == 'provider')
    consumer = sum(1 for f in findings if f.get('responsible') == 'consumer')
    total = len(findings)

    risk_score = 0 if total == 0 else min(100, (critical * 30 + warning * 10) / total * 20)
    compliance = max(0, 100 - (critical * 15 + warning * 5))

    return {
        "risk_score": round(risk_score, 2),
        "compliance_percent": round(compliance, 2),
        "critical_findings": critical,
        "warning_findings": warning,
        "provider_issues": provider,
        "consumer_issues": consumer,
        "total_findings": total,
        "timestamp": datetime.now().isoformat(),
        "findings": findings
    }


def create_visualization(metrics):
    charts_dir = os.path.join(settings.BASE_DIR, 'static', 'charts')
    os.makedirs(charts_dir, exist_ok=True)

    # График ответственности
    if metrics['provider_issues'] > 0 or metrics['consumer_issues'] > 0:
        plt.figure(figsize=(8, 6))
        plt.pie([metrics['provider_issues'], metrics['consumer_issues']],
                labels=['Поставщик', 'Потребитель'], autopct='%1.1f%%',
                colors=['#3498db', '#e74c3c'])
        plt.title('Распределение ответственности\nВариант 32')
        plt.savefig(os.path.join(charts_dir, 'responsibility.png'))
        plt.close()

    # График критичности
    if metrics['critical_findings'] > 0 or metrics['warning_findings'] > 0:
        plt.figure(figsize=(8, 6))
        plt.pie([metrics['critical_findings'], metrics['warning_findings']],
                labels=['Критические', 'Предупреждения'], autopct='%1.1f%%',
                colors=['#e74c3c', '#f39c12'])
        plt.title('Степень критичности нарушений')
        plt.savefig(os.path.join(charts_dir, 'severity.png'))
        plt.close()

    # График риска
    plt.figure(figsize=(10, 4))
    risk = metrics['risk_score']
    color = '#27ae60' if risk < 30 else '#f39c12' if risk < 70 else '#e74c3c'
    plt.barh(0, risk, color=color)
    plt.barh(0, 100, color='lightgray', alpha=0.3)
    plt.xlim(0, 100)
    plt.yticks([])
    plt.xlabel('Risk Score')
    plt.title(f'Уровень риска: {risk}/100')
    plt.savefig(os.path.join(charts_dir, 'risk.png'))
    plt.close()