# Generated by Django 4.1.4 on 2022-12-19 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notificator', '0002_alter_customer_time_zone_alter_message_created_at_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ['id'], 'verbose_name': 'Клиент', 'verbose_name_plural': 'Клиенты'},
        ),
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['id'], 'verbose_name': 'Сообщение', 'verbose_name_plural': 'Сообщения'},
        ),
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['start_at'], 'verbose_name': 'Рассылка', 'verbose_name_plural': 'Рассылки'},
        ),
        migrations.AlterField(
            model_name='message',
            name='status',
            field=models.CharField(choices=[('pending', 'В очереди на отправку'), ('sent', 'Отправлено'), ('failed', 'Ошибка отправки'), ('timed_out', 'Не успели отправить')], max_length=100, verbose_name='Статус'),
        ),
    ]
