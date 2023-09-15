import os
import shutil

from django.core.management import call_command
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, TemplateView, FormView

from crm.domain.service.reports.reportlayout1 import ReportLayout1
from crm.domain.repository.landrepository import LandRepository
from crm.domain.service.zipfileservice import ZipFileService
from crm.forms import CompanyCreateForm, LandCreateForm, UploadZipForm
from crm.models import Company, Land, LandScoreChemical, LandReview, CompanyCategory, LandLedger, \
    SoilHardnessMeasurementImportErrors, SoilHardnessMeasurement, LandBlock


class Home(TemplateView):
    template_name = "crm/home.html"


class CompanyListView(ListView):
    model = Company
    template_name = "crm/company/list.html"

    def get_queryset(self):
        return super().get_queryset().filter(category=CompanyCategory.AGRI_COMPANY)


class CompanyCreateView(CreateView):
    model = Company
    template_name = "crm/company/create.html"
    form_class = CompanyCreateForm

    def get_success_url(self):
        return reverse('crm:company_detail', kwargs={'pk': self.object.pk})


class CompanyDetailView(DetailView):
    model = Company
    template_name = 'crm/company/detail.html'


class LandListView(ListView):
    model = Land
    template_name = "crm/land/list.html"

    def get_queryset(self):
        company = Company(pk=self.kwargs['company_id'])
        return super().get_queryset().filter(company=company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = Company(pk=self.kwargs['company_id'])
        land_repository = LandRepository(company)
        land_ledger_map = {land: land_repository.read_landledgers(land) for land in context['object_list']}
        context['company'] = company
        context['land_ledger_map'] = land_ledger_map

        return context


class LandCreateView(CreateView):
    model = Land
    template_name = "crm/land/create.html"
    form_class = LandCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = Company(pk=self.kwargs['company_id'])
        context['company'] = company

        return context

    def form_valid(self, form):
        form.instance.company_id = self.kwargs['company_id']

        return super().form_valid(form)

    def get_success_url(self):
        company = Company(pk=self.kwargs['company_id'])
        return reverse('crm:land_detail', kwargs={'company_id': company.id, 'pk': self.object.pk})


class LandDetailView(DetailView):
    model = Land
    template_name = 'crm/land/detail.html'


class LandReportChemicalListView(ListView):
    model = LandScoreChemical
    template_name = "crm/landreport/chemical.html"

    def get_queryset(self):
        landledger = LandLedger(self.kwargs['landledger_id'])
        return super().get_queryset().filter(landledger=landledger)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        landledger = LandLedger.objects.get(id=self.kwargs['landledger_id'])

        context['charts'] = ReportLayout1(landledger).publish()
        context['company'] = Company(self.kwargs['company_id'])
        context['landledger'] = landledger
        context['landscores'] = LandScoreChemical.objects.filter(landledger=landledger)
        context['landreview'] = LandReview.objects.filter(landledger=landledger)

        return context


class UploadSoilhardnessView(FormView):
    template_name = 'crm/soilhardness/upload/form.html'
    form_class = UploadZipForm
    success_url = reverse_lazy('crm:upload_soilhardness_success')

    def form_valid(self, form):
        # Zipを処理してバッチ実行
        upload_folder = ZipFileService.handle_uploaded_zip(self.request.FILES['zipfile'])
        if os.path.exists(upload_folder):
            call_command('import_soil_hardness', upload_folder)
            shutil.rmtree(upload_folder)

        return super().form_valid(form)


class UploadZipSuccessView(TemplateView):
    template_name = 'crm/soilhardness/upload/success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['import_errors'] = SoilHardnessMeasurementImportErrors.objects.all()
        return context


class AssociationView(ListView):
    model = SoilHardnessMeasurement
    template_name = 'crm/soilhardness/association/list.html'

    def get_queryset(self, **kwargs):
        return super().get_queryset() \
            .filter(landblock__isnull=True) \
            .values('setmemory', 'setdatetime') \
            .annotate(cnt=Count('id')) \
            .order_by('setmemory')

    @staticmethod
    def post(request, **kwargs):
        # TODO: R をつけた25レコードに対して5レコードずつ順に C1, C3, A3, B2, A1 を付与
        #  リストにappendしてバルク更新
        checkboxes = request.POST.getlist('checkboxes[]')
        print(f'checkboxes: {checkboxes}')

        return HttpResponseRedirect(reverse('crm:association_success'))


class AssociationIndividualView(ListView):
    model = SoilHardnessMeasurement
    template_name = 'crm/soilhardness/association/individual/list.html'

    def get_queryset(self, **kwargs):
        first_memory_number = self.kwargs.get('memory_anchor')
        return super().get_queryset() \
            .filter(setmemory__range=(first_memory_number, first_memory_number + 24)) \
            .values('setmemory', 'setdatetime') \
            .annotate(cnt=Count('id')) \
            .order_by('setmemory')

    def get_context_data(self, **kwargs):
        first_memory_number = self.kwargs.get('memory_anchor')
        context = super().get_context_data(**kwargs)
        context['memory_anchor'] = first_memory_number
        context['land_blocks'] = LandBlock.objects.order_by('id').all()
        return context

    @staticmethod
    def post(request, **kwargs):
        # TODO: first_memory_number を含んで25レコードに C1, C3, A3, B2, A1 を適用
        #  リストにappendしてバルク更新
        first_memory_number = kwargs.get('memory_anchor')
        landblocks = request.POST.getlist('landblocks[]')
        print(f'landblocks: {landblocks}')

        return HttpResponseRedirect(reverse('crm:association'))


class AssociationSuccessView(TemplateView):
    template_name = 'crm/soilhardness/association/success.html'


class RouteSuggestUploadView(TemplateView):
    template_name = 'crm/routesuggest/form.html'


class RouteSuggestSuccessView(TemplateView):
    template_name = 'crm/routesuggest/success.html'
    # TODO:
    #  step1: xarvioで任意の圃場をKMLダウンロード
    #  step2: KMLをアップロードして圃場のリストを作る（名称ではgooglemapでdirectionできないから、座標でもいいのかな）
    #   KMLを読む（未使用の）ロジックはあるね crm/tests/domain/service/test_landcandidateservice.py
    #   ["B0", "B2", "B4", "C5", "そば2", "リヴァンプ2", "ローソン4", "伊佐地4", "湖東中4", "山崎開発1", "小澤農園", "上4", "東大山1"]
    #  step3: success.html から呼ばれる gmap_direction に、出発地、経由地（最大８）、到着地で当て込む
    #  step4: 作業指示書としての体裁を整える
