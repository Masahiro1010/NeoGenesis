# Generated by Django 5.2.4 on 2025-07-03 01:23

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GameSession",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("final_score", models.IntegerField(blank=True, null=True)),
                ("current_ante_number", models.IntegerField(default=1)),
                ("gold", models.IntegerField(default=10)),
                ("deck_numbers", models.JSONField(default=list)),
                ("used_cards", models.JSONField(default=list)),
            ],
        ),
        migrations.CreateModel(
            name="Card",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "card_type",
                    models.CharField(
                        choices=[
                            ("joker", "ジョーカー"),
                            ("tarot", "タロット"),
                            ("spectral", "スペクトル"),
                            ("item", "アイテム"),
                        ],
                        max_length=20,
                    ),
                ),
                ("card_name", models.CharField(max_length=50)),
                (
                    "slot_type",
                    models.CharField(
                        choices=[
                            ("joker", "ジョーカースロット"),
                            ("consumable", "消費スロット"),
                        ],
                        max_length=20,
                    ),
                ),
                ("is_used", models.BooleanField(default=False)),
                ("target_number", models.IntegerField(blank=True, null=True)),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cards",
                        to="game.gamesession",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Round",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ante_number", models.IntegerField()),
                ("answer_code", models.CharField(max_length=4)),
                ("score_total", models.IntegerField(default=0)),
                ("shop_choices", models.JSONField(default=dict)),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rounds",
                        to="game.gamesession",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Guess",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("guess_code", models.CharField(max_length=4)),
                ("hit", models.IntegerField()),
                ("blow", models.IntegerField()),
                ("role_score", models.IntegerField()),
                ("card_score", models.IntegerField()),
                ("total_score", models.IntegerField()),
                (
                    "round",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="guesses",
                        to="game.round",
                    ),
                ),
            ],
        ),
    ]
