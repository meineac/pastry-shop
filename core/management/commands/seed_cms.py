"""
Management command: seed_cms

Seeds the database with CMS content: company info, news (with images),
vacancies, Q&A entries, partners, and promotional banners.

Run with:
    python manage.py seed_cms
"""

import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from cms.models import CompanyInfo, News, Vacancy, QaA, Partner, PromotionalBanner
from core.management.seed_data.cms import (
    COMPANY_INFO,
    NEWS_ITEMS,
    QNA_ITEMS,
    VACANCIES,
    PARTNERS,
    BANNERS,
)
from core.management.seed_data.images import link_news_images

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Seed CMS: company info, news (with images), vacancies, Q&A, partners, banners."

    @transaction.atomic
    def handle(self, *args, **options):
        self._seed_company_info()
        self._seed_news()
        self._seed_vacancies()
        self._seed_qna()
        self._seed_partners()
        self._seed_banners()
        self.stdout.write(self.style.SUCCESS("CMS seeded successfully!"))

    # ------------------------------------------------------------------
    # Company Info
    # ------------------------------------------------------------------

    def _seed_company_info(self):
        self.stdout.write("Seeding company info...")
        if not CompanyInfo.objects.exists():
            # Remove logo from dict — it's linked separately
            info = {k: v for k, v in COMPANY_INFO.items() if k != 'logo'}
            CompanyInfo.objects.create(**info)
            self.stdout.write("  Created company info.")
        else:
            # Update new fields if they exist but are blank
            obj = CompanyInfo.objects.first()
            changed = False
            for field in ('video_url', 'certificate_text'):
                if not getattr(obj, field, None):
                    setattr(obj, field, COMPANY_INFO.get(field, ''))
                    changed = True
            if changed:
                obj.save()
                self.stdout.write("  Updated company info with new fields.")
            else:
                self.stdout.write("  Company info already exists.")

        # Link company logo
        logo_path = os.path.join(settings.MEDIA_ROOT, 'company', 'logo.jpg')
        if os.path.exists(logo_path):
            obj = CompanyInfo.objects.first()
            if obj and not obj.logo:
                obj.logo.name = 'company/logo.jpg'
                obj.save(update_fields=['logo'])
                self.stdout.write("  Linked company logo.")

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

    # ------------------------------------------------------------------
    # Partners
    # ------------------------------------------------------------------

    def _seed_partners(self):
        self.stdout.write("Seeding partner companies...")
        for item in PARTNERS:
            partner, created = Partner.objects.get_or_create(
                name=item["name"],
                defaults={"website_url": item["website"]},
            )
            if created or not partner.logo:
                logo_path = os.path.join(settings.MEDIA_ROOT, item["logo"])
                if os.path.exists(logo_path):
                    partner.logo.name = item["logo"]
                    partner.save(update_fields=['logo'])
                    self.stdout.write(f"  Created/linked partner: {partner.name}")
                else:
                    self.stdout.write(f"  Created partner (no logo found): {partner.name}")

    # ------------------------------------------------------------------
    # Promotional Banners
    # ------------------------------------------------------------------

    def _seed_banners(self):
        self.stdout.write("Seeding promotional banners...")
        for item in BANNERS:
            banner, created = PromotionalBanner.objects.get_or_create(
                title=item["title"],
                defaults={"position": item["position"]},
            )
            if created or not banner.image:
                img_path = os.path.join(settings.MEDIA_ROOT, item["image"])
                if os.path.exists(img_path):
                    banner.image.name = item["image"]
                    banner.save(update_fields=['image'])
                    self.stdout.write(f"  Created/linked banner: {banner.title}")
                else:
                    self.stdout.write(f"  Banner image not found: {item['image']}")
