import io
import zipfile
from unittest import mock

import PyPDF2
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.test import TestCase
from django.urls import NoReverseMatch, reverse

from .models import PlanDocument, PlanSet


def pdf_bytes(pages):
    writer = PyPDF2.PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=100, height=100)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


class RemoteStorage(Storage):
    """Behaves like Cloudinary: no local paths (Storage.path raises) and absolute URLs."""

    def __init__(self):
        self.files = {}

    def _open(self, name, mode='rb'):
        return ContentFile(self.files[name], name=name)

    def _save(self, name, content):
        self.files[name] = b''.join(content.chunks())
        return name

    def exists(self, name):
        return name in self.files

    def url(self, name):
        return f'https://cdn.example.com/{name}'


class PlanRoomTestCase(TestCase):
    def setUp(self):
        storage = RemoteStorage()
        for field_name in ('pdf_file', 'preview_pdf'):
            patcher = mock.patch.object(PlanDocument._meta.get_field(field_name), 'storage', storage)
            patcher.start()
            self.addCleanup(patcher.stop)

        self.user = User.objects.create_user('client', 'client@example.com', 'pw')
        self.plan_set = PlanSet.objects.create(title='Bridge Plans', description='d', access_type='clients', preview_pages=2)
        self.document = PlanDocument(plan_set=self.plan_set, document_number=1)
        self.document.pdf_file.save('bridge.pdf', ContentFile(pdf_bytes(5)))
        self.document.refresh_from_db()

    def make_free(self):
        PlanSet.objects.filter(id=self.plan_set.id).update(access_type='free')


class RemovedPaymentTests(PlanRoomTestCase):
    def test_payment_routes_are_gone(self):
        for name, args in (('checkout', [self.plan_set.id]), ('dashboard', [])):
            with self.assertRaises(NoReverseMatch):
                reverse(name, args=args)
        self.assertEqual(self.client.get(f'/plan-room/checkout/{self.plan_set.id}/').status_code, 404)
        self.assertEqual(self.client.get('/plan-room/dashboard/').status_code, 404)

    def test_paid_is_no_longer_an_access_type(self):
        self.assertEqual([value for value, _ in PlanSet.ACCESS_CHOICES], ['free', 'clients'])

    def test_details_page_has_no_full_pdf_buy_or_price(self):
        body = self.client.get(reverse('plan_set_detail', args=[self.plan_set.id])).content.decode()
        self.assertNotIn(self.document.pdf_file.url, body)
        for text in ('View Full PDF', 'Buy Full Access', 'Login to Buy', 'Download Full Set', '$'):
            self.assertNotIn(text, body)
        self.assertIn('View Preview', body)
        self.assertIn('Clients Only', body)


class PreviewTests(PlanRoomTestCase):
    def preview(self):
        return self.client.get(reverse('preview_document', args=[self.document.id]))

    def test_clients_only_plan_returns_only_the_preview(self):
        self.client.force_login(self.user)
        response = self.preview()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['pdf_url'], self.document.preview_pdf.url)
        self.assertNotEqual(response.json()['pdf_url'], self.document.pdf_file.url)

    def test_preview_is_limited_to_preview_pages_and_flat_name(self):
        self.assertEqual(self.document.preview_pdf.name.count('/'), 1)
        with self.document.preview_pdf.open('rb') as preview:
            self.assertEqual(len(PyPDF2.PdfReader(io.BytesIO(preview.read())).pages), 2)

    def test_missing_preview_is_generated_on_request(self):
        PlanDocument.objects.filter(id=self.document.id).update(preview_pdf='')
        self.assertEqual(self.preview().status_code, 200)
        self.document.refresh_from_db()
        self.assertTrue(self.document.preview_pdf)

    def test_free_plan_returns_full_pdf(self):
        self.make_free()
        self.assertEqual(self.preview().json()['pdf_url'], self.document.pdf_file.url)


class DownloadTests(PlanRoomTestCase):
    def download(self):
        return self.client.get(reverse('download_set', args=[self.plan_set.id]))

    def test_anonymous_user_is_sent_to_login(self):
        response = self.download()
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_clients_only_plan_is_denied(self):
        self.client.force_login(self.user)
        self.assertRedirects(self.download(), reverse('plan_set_detail', args=[self.plan_set.id]))

    def test_free_plan_gives_a_valid_zip(self):
        self.make_free()
        self.client.force_login(self.user)
        response = self.download()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertIn('bridge-plans.zip', response['Content-Disposition'])
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            self.assertEqual(archive.namelist(), ['bridge-plans_Doc1.pdf'])
            pdf = PyPDF2.PdfReader(io.BytesIO(archive.read('bridge-plans_Doc1.pdf')))
            self.assertEqual(len(pdf.pages), 5)

    def test_storage_failure_shows_message_instead_of_crashing(self):
        self.make_free()
        self.client.force_login(self.user)
        storage = PlanDocument._meta.get_field('pdf_file').storage
        with mock.patch.object(storage, '_open', side_effect=OSError('unavailable')):
            response = self.client.get(reverse('download_set', args=[self.plan_set.id]), follow=True)
        self.assertEqual(response.redirect_chain[-1][0], reverse('plan_set_detail', args=[self.plan_set.id]))
        self.assertContains(response, 'could not be downloaded')
