"""
Модели базы данных для системы проверки безопасности облака
Вариант 32 - Контейнер безопасности облака
"""

from django.db import models
from django.utils import timezone


class TestProtocol(models.Model):
    PROTOCOL_STATUS = [
        ('SUCCESS', 'Успешно'),
        ('WARNING', 'С предупреждениями'),
        ('FAILED', 'Провален'),
        ('IN_PROGRESS', 'В процессе'),
    ]

    protocol_number = models.CharField(max_length=50, unique=True, verbose_name="Номер протокола")
    test_date = models.DateTimeField(default=timezone.now, verbose_name="Дата тестирования")
    tester_name = models.CharField(max_length=100, default="Студент", verbose_name="Тестировщик")
    status = models.CharField(max_length=20, choices=PROTOCOL_STATUS, default='IN_PROGRESS', verbose_name="Статус")
    total_checks = models.IntegerField(default=0, verbose_name="Всего проверок")
    passed_checks = models.IntegerField(default=0, verbose_name="Пройдено проверок")
    failed_checks = models.IntegerField(default=0, verbose_name="Провалено проверок")
    risk_score = models.FloatField(default=0.0, verbose_name="Оценка риска")
    compliance_percent = models.FloatField(default=0.0, verbose_name="Процент соответствия")
    detailed_results = models.JSONField(default=dict, verbose_name="Детальные результаты")
    recommendations = models.TextField(blank=True, verbose_name="Рекомендации")
    test_duration = models.FloatField(default=0.0, verbose_name="Длительность теста (сек)")

    class Meta:
        verbose_name = "Протокол тестирования"
        verbose_name_plural = "Протоколы тестирования"
        ordering = ['-test_date']

    def __str__(self):
        return f"Протокол №{self.protocol_number} от {self.test_date.strftime('%d.%m.%Y %H:%M')}"

    def generate_protocol_number(self):
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")
        count = TestProtocol.objects.filter(protocol_number__startswith=f"SEC-{date_str}").count()
        return f"SEC-{date_str}-{count+1:04d}"

    def save(self, *args, **kwargs):
        if not self.protocol_number:
            self.protocol_number = self.generate_protocol_number()
        super().save(*args, **kwargs)


class SecurityFinding(models.Model):
    SEVERITY_LEVELS = [
        ('CRITICAL', 'Критический'),
        ('HIGH', 'Высокий'),
        ('MEDIUM', 'Средний'),
        ('WARNING', 'Предупреждение'),
        ('INFO', 'Информационный'),
    ]

    RESPONSIBILITY = [
        ('provider', 'Поставщик'),
        ('consumer', 'Потребитель'),
        ('shared', 'Совместная'),
    ]

    protocol = models.ForeignKey(TestProtocol, on_delete=models.CASCADE, related_name='findings', verbose_name="Протокол")
    resource_name = models.CharField(max_length=200, verbose_name="Ресурс")
    resource_type = models.CharField(max_length=50, verbose_name="Тип ресурса")
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, verbose_name="Критичность")
    finding_message = models.TextField(verbose_name="Описание находки")
    remediation = models.TextField(verbose_name="Рекомендации по устранению")
    responsibility = models.CharField(max_length=20, choices=RESPONSIBILITY, verbose_name="Ответственность")
    detection_time = models.DateTimeField(auto_now_add=True, verbose_name="Время обнаружения")
    resolved = models.BooleanField(default=False, verbose_name="Устранено")
    resolution_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата устранения")

    class Meta:
        verbose_name = "Находка безопасности"
        verbose_name_plural = "Находки безопасности"
        ordering = ['-severity', '-detection_time']

    def __str__(self):
        return f"[{self.severity}] {self.resource_name}: {self.finding_message[:50]}"


class TestDataset(models.Model):
    DATASET_TYPES = [
        ('STORAGE', 'Хранилища'),
        ('IAM', 'Права доступа'),
        ('SLA', 'SLA провайдера'),
        ('ENCRYPTION', 'Шифрование'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name="Название набора")
    dataset_type = models.CharField(max_length=20, choices=DATASET_TYPES, verbose_name="Тип данных")
    description = models.TextField(verbose_name="Описание")
    test_data = models.JSONField(verbose_name="Тестовые данные")
    expected_results = models.JSONField(default=dict, verbose_name="Ожидаемые результаты")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Тестовый набор данных"
        verbose_name_plural = "Тестовые наборы данных"
        ordering = ['dataset_type', 'name']

    def __str__(self):
        return f"{self.get_dataset_type_display()}: {self.name}"


class SecurityCheckRule(models.Model):
    rule_id = models.CharField(max_length=50, unique=True, verbose_name="ID правила")
    name = models.CharField(max_length=200, verbose_name="Название правила")
    category = models.CharField(max_length=50, verbose_name="Категория")
    description = models.TextField(verbose_name="Описание")
    severity = models.CharField(max_length=20, choices=SecurityFinding.SEVERITY_LEVELS, verbose_name="Критичность")
    check_logic = models.TextField(verbose_name="Логика проверки")
    remediation_template = models.TextField(verbose_name="Шаблон рекомендации")
    responsibility = models.CharField(max_length=20, choices=SecurityFinding.RESPONSIBILITY, default='consumer', verbose_name="Ответственность")
    is_enabled = models.BooleanField(default=True, verbose_name="Включено")
    priority = models.IntegerField(default=0, verbose_name="Приоритет")

    class Meta:
        verbose_name = "Правило проверки"
        verbose_name_plural = "Правила проверки"
        ordering = ['category', 'priority']

    def __str__(self):
        return f"{self.rule_id}: {self.name}"