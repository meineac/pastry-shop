"""
Management command: seed_cms

Seeds the database with CMS content: company info, news (with images),
vacancies, and Q&A entries.

Run with:
    python manage.py seed_cms
"""

import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from cms.models import CompanyInfo, News, Vacancy, QaA
from core.management.seed_data.cms import (
    COMPANY_INFO,
    NEWS_ITEMS,
    QNA_ITEMS,
    VACANCIES,
)
from core.management.seed_data.images import link_news_images

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Seed CMS: company info, news (with images), vacancies, Q&A."

    @transaction.atomic
    def handle(self, *args, **options):
        self._seed_company_info()
        self._seed_news()
        self._seed_vacancies()
        self._seed_qna()
        self.stdout.write(self.style.SUCCESS("CMS seeded successfully!"))

    # ------------------------------------------------------------------
    # Company Info
    # ------------------------------------------------------------------

    def _seed_company_info(self):
        self.stdout.write("Seeding company info...")
        if not CompanyInfo.objects.exists():
            CompanyInfo.objects.create(**COMPANY_INFO)
            self.stdout.write("  Created company info.")
        else:
            self.stdout.write("  Company info already exists.")

    # ------------------------------------------------------------------
    # News
    # ------------------------------------------------------------------

    def _seed_news(self):
        self.stdout.write("Seeding news articles...")
        for item in NEWS_ITEMS:
            News.objects.get_or_create(
                title=item["title"],
                defaults={
                    "short_summary": item["summary"],
                    "full_text": item["text"],
                },
            )

        self.stdout.write("Linking news images...")
        link_news_images(self.stdout)

    # ------------------------------------------------------------------
    # Vacancies
    # ------------------------------------------------------------------

    def _seed_vacancies(self):
        self.stdout.write("Seeding vacancies...")
        for item in VACANCIES:
            Vacancy.objects.get_or_create(
                title=item["title"],
                defaults={"description": item["desc"]},
            )

    # ------------------------------------------------------------------
    # Q&A
    # ------------------------------------------------------------------

    def _seed_qna(self):
        self.stdout.write("Seeding Q&A entries...")
        for item in QNA_ITEMS:
            QaA.objects.get_or_create(
                question_text=item["q"],
                defaults={"answer_text": item["a"]},
            )
