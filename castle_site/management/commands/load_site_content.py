"""Load the approved website copy from the client's content package (6 November 2026).

Only content the client actually supplied is loaded. Anything still marked [SUPPLY] in the
package (logo, photos, team directory, social links, statistics, testimonials, partners)
is left out, and the templates hide those sections while they are empty.

Safe to run repeatedly: existing records are left alone so admin edits are kept.
Pass --update to overwrite the text of existing records with this copy. Images are
never touched.
"""
from datetime import datetime, timedelta, timezone as dt_timezone

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from castle_site.models import (
    CompanyHighlight, ContactInfo, Group, HeroImages, Our_Mission_Vision_Statement,
    Projects, Services, Team,
)

CONTACT = {
    'address': 'Rehab, Paynesville City, Montserrado County, Liberia',
    'phone': '+231 777 176 236, +231 881 937 361',
    'email': 'castlegroupof@gmail.com',
}

HERO = {
    'hero_title': 'Building with Purpose. Delivering with Integrity.',
    'hero_paragraph': (
        '<p>From residential and commercial construction to infrastructure works, security and '
        'operational support, Castle Group of Companies helps clients plan, build, protect and '
        'maintain valuable assets across Liberia.</p>'
    ),
}

ABOUT = {
    'founder_fullname': 'Prince Kollie',
    'founder_title': 'Founder and CEO',
    'founder_quote': (
        'Our responsibility is to turn each client’s vision into practical results through '
        'careful planning, quality work and honest relationships.'
    ),
    'slogan': 'Building Infrastructure. Securing Futures. Delivering Excellence.',
    'year_founded_est': datetime(2017, 1, 1, tzinfo=dt_timezone.utc),
    'our_purpose': (
        '<p>Established in 2017, Castle Group of Companies is a Liberian-owned enterprise '
        'headquartered in Paynesville, Montserrado County. The company provides integrated '
        'construction, civil engineering, infrastructure, security, logistics, consultancy and '
        'facility support solutions. Our approach emphasizes practical planning, accountable '
        'project delivery, safety and lasting client relationships.</p>'
    ),
    'history': (
        '<p>Castle Group of Companies began operations in 2017 in Liberia with a focus on meeting '
        'practical needs in construction and general contracting. As client needs evolved, the '
        'company expanded its service offering to cover civil engineering, infrastructure-related '
        'works, road maintenance, security, logistics, facility services and project '
        'consultancy.</p>'
        '<p>Operating from Paynesville, Montserrado County, Castle works with private clients, '
        'businesses and institutions on assignments ranging from building construction and '
        'renovations to sanitation facilities, perimeter works and project supervision. The '
        'company continues to strengthen its technical partnerships and team capabilities as it '
        'pursues additional opportunities in Liberia and the wider region.</p>'
    ),
    'mission_statement': (
        '<p>To deliver safe, reliable and cost-conscious construction, engineering and support '
        'services that meet client requirements and contribute to sustainable development.</p>'
    ),
    'vision_statement': (
        '<p>To become a trusted Liberian and regional partner for quality infrastructure, secure '
        'facilities and integrated business solutions.</p>'
    ),
    'our_values': (
        '<ul>'
        '<li>Integrity and accountability in our commitments</li>'
        '<li>Quality workmanship and practical innovation</li>'
        '<li>Safety and respect for people</li>'
        '<li>Professional teamwork and timely communication</li>'
        '<li>Client service and responsible stewardship of resources</li>'
        '</ul>'
    ),
}

LEADERSHIP = [
    {
        'fullname': 'Prince Kollie',
        'title': 'Founder and Chief Executive Officer',
        'bio': (
            '<p>Prince founded the business in 2017 and leads its strategic direction, client '
            'relationships and business development. His experience spans construction-related '
            'operations and security management.</p>'
        ),
    },
]

HIGHLIGHTS = [
    ('Liberian-owned, established in 2017', 'fas fa-flag'),
    ('Headquartered in Paynesville, Montserrado County', 'fas fa-map-marker-alt'),
    ('Construction, engineering, security, logistics and facility services', 'fas fa-check-circle'),
]

# (title, category, description)
SERVICES = [
    ('Building Construction and Renovation', 'Construction',
     'Construction of residential, commercial and institutional buildings, including structural '
     'works, finishing and building improvement assignments.'),
    ('Civil Engineering and Infrastructure', 'Engineering',
     'Civil works, site development, drainage-related infrastructure and engineering coordination '
     'for private and institutional projects.'),
    ('Road Construction and Maintenance', 'Infrastructure',
     'Site clearing, earthworks, road preparation, grading, laterite and aggregate placement and '
     'associated maintenance activities, subject to the approved project scope.'),
    ('Security Guard Services and Risk Support', 'Security',
     'Security personnel deployment, site access control, property protection, security planning '
     'and operational risk assessments.'),
    ('Project Management and Consultancy', 'Consulting',
     'Construction planning, project coordination, technical advisory support, supervision, '
     'procurement support and stakeholder reporting.'),
    ('Logistics and Transportation', 'Logistics',
     'Transport coordination, material movement, vehicle rental and logistical support for field '
     'operations and projects.'),
    ('Janitorial and Facility Management', 'Facilities',
     'Routine cleaning, site housekeeping, facility upkeep and related services for commercial or '
     'institutional premises.'),
    ('Perimeter Fencing and Site Works', 'Construction',
     'Boundary walls, fencing, gates and associated groundworks to improve property definition and '
     'site security.'),
]

# (title, type, location or None, description), in the order the package lists them.
PROJECTS = [
    ('Montserrado County Health Team Headquarters', 'Institutional', 'Bensonville, Montserrado County',
     'Multi-level health administration headquarters construction. Ongoing.'),
    ('Grand Bassa and Montserrado Health Team Sanitation Works', 'Institutional',
     'Grand Bassa and Montserrado Counties',
     'Bathroom and pit works associated with health team facilities.'),
    ('Nine-Apartment Residential Building', 'Residential', None,
     'Multi-unit residential building of approximately 100 by 40 feet.'),
    ('Perimeter Wall and Fencing Projects', 'Site Works', None,
     'Boundary and fencing works across private sites.'),
    ('Commercial Warehouse', 'Commercial', None,
     'Warehouse project of approximately 60 by 20 feet.'),
    ('Mixed-Use Building Proposal', 'Proposed', 'Congo Town Back Road, Monrovia',
     'Proposed five-storey mixed-use concept for a roughly 60 by 120 foot site.'),
    ('Castle Real Estate Development', 'Proposed', 'Lower Margibi County',
     'Proposed 100-acre real estate development concept near Roberts International Airport.'),
]


def _group(name):
    group, _ = Group.objects.get_or_create(name=name, defaults={'display_name': name})
    return group


class Command(BaseCommand):
    help = 'Load the approved Castle Group of Companies website copy. Safe to run repeatedly.'

    def add_arguments(self, parser):
        parser.add_argument('--update', action='store_true',
                            help='Overwrite the text of existing records with this copy.')

    @transaction.atomic
    def handle(self, *args, update=False, **options):
        self.update = update
        self.created = self.updated = 0

        self._singleton(ContactInfo, CONTACT)
        self._singleton(Our_Mission_Vision_Statement, ABOUT)
        self._upsert(HeroImages, {'hero_title': HERO['hero_title']}, HERO)

        for member in LEADERSHIP:
            self._upsert(Team, {'fullname': member['fullname']}, member)

        for order, (text, icon) in enumerate(HIGHLIGHTS):
            self._upsert(CompanyHighlight, {'text': text}, {'icon_class': icon, 'order': order})

        for title, category, description in SERVICES:
            self._upsert(Services, {'title': title},
                         {'group': _group(category), 'description': f'<p>{description}</p>'})

        # The projects page lists newest first, so new projects get descending timestamps
        # (created_at is auto_now_add and can only be changed with update()).
        now = timezone.now()
        for position, (title, kind, location, description) in enumerate(PROJECTS):
            body = f'<p>{description}</p>'
            if location:
                body = f'<p><strong>Location:</strong> {location}</p>' + body
            obj, created = self._upsert(Projects, {'title': title},
                                        {'group': _group(kind), 'description': body})
            if created:
                Projects.objects.filter(pk=obj.pk).update(created_at=now - timedelta(minutes=position))

        self.stdout.write(self.style.SUCCESS(
            f'Site content loaded: {self.created} created, {self.updated} updated.'))

    def _singleton(self, model, values):
        obj = model.objects.first()
        if obj is None:
            model.objects.create(**values)
            self.created += 1
        elif self.update:
            for key, value in values.items():
                setattr(obj, key, value)
            obj.save()
            self.updated += 1

    def _upsert(self, model, lookup, values):
        obj = model.objects.filter(**lookup).first()
        if obj is None:
            self.created += 1
            return model.objects.create(**{**values, **lookup}), True
        if self.update:
            for key, value in values.items():
                setattr(obj, key, value)
            obj.save()
            self.updated += 1
        return obj, False
