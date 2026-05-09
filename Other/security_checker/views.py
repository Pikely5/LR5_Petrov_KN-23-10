from django.shortcuts import render
from .security_logic import SecurityChecker, calculate_metrics, create_visualization

def index(request):
    context = {
        'title': 'Контейнер безопасности облака - Вариант 32',
        'author': 'Иванов И.И.',  # ЗАМЕНИТЕ НА СВОЮ ФАМИЛИЮ!
    }

    if request.method == 'POST':
        checker = SecurityChecker()
        findings = checker.run_full_check()
        metrics = calculate_metrics(findings)
        create_visualization(metrics)

        findings_html = ""
        for finding in metrics.get("findings", []):
            severity_class = "critical" if finding.get("severity") == "CRITICAL" else "warning"
            responsible_text = "Потребитель" if finding.get("responsible") == "consumer" else "Поставщик"

            findings_html += f"""
            <li class='{severity_class}'>
                <strong>[{finding.get('severity')}]</strong> {finding.get('resource')}: {finding.get('message')}<br>
                <small>Рекомендация: {finding.get('remediation')} | Ответственный: {responsible_text}</small>
            </li>
            """

        context.update({
            'metrics': metrics,
            'findings_html': findings_html,
            'has_results': True,
        })
    else:
        context['has_results'] = False

    return render(request, 'security_checker/index.html', context)