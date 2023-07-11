import os
import shutil

from django.core.management import call_command
from django.db.models import Avg
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, TemplateView, FormView

from crm.domain.graph.graph_matplotlib import GraphMatplotlib
from crm.domain.repository.landrepository import LandRepository
from crm.domain.services.zipfileservice import ZipFileService
from crm.forms import CompanyCreateForm, LandCreateForm, UploadZipForm
from crm.models import Company, Land, LandScoreChemical, LandReview, CompanyCategory, LandLedger, \
    SoilHardnessMeasurementImportErrors


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
        landscores = LandScoreChemical.objects.filter(landledger=landledger)

        # LandScoreChemical
        land_scores_agg = landscores.aggregate(
            Avg('ec'), Avg('nh4n'), Avg('no3n'), Avg('total_nitrogen'), Avg('nh4_per_nitrogen'),
            Avg('ph'), Avg('cao'), Avg('mgo'), Avg('k2o'), Avg('base_saturation'), Avg('cao_per_mgo'),
            Avg('mgo_per_k2o'), Avg('phosphorus_absorption'), Avg('p2o5'), Avg('cec'), Avg('humus'),
            Avg('bulk_density'),
        )

        g = GraphMatplotlib()
        x = ['EC(mS/cm)', 'NH4-N(mg/100g)', 'NO3-N(mg/100g)', '無機態窒素', 'NH4/無機態窒素', ' ', '  ']
        y = [
            land_scores_agg['ec__avg'],
            land_scores_agg['nh4n__avg'],
            land_scores_agg['no3n__avg'],
            land_scores_agg['total_nitrogen__avg'],
            land_scores_agg['nh4_per_nitrogen__avg'],
            0,
            0
        ]
        chart1 = g.plot_graph("窒素関連（1圃場の全エリア平均）", x, y)

        x = ['ph', 'CaO(mg/100g)', 'MgO(mg/100g)', 'K2O(mg/100g)', '塩基飽和度(%)', 'CaO/MgO', 'MgO/K2O']
        y = [
            land_scores_agg['ph__avg'],
            land_scores_agg['cao__avg'],
            land_scores_agg['mgo__avg'],
            land_scores_agg['k2o__avg'],
            land_scores_agg['base_saturation__avg'],
            land_scores_agg['cao_per_mgo__avg'],
            land_scores_agg['mgo_per_k2o__avg']
        ]
        chart2 = g.plot_graph("塩基類関連（1圃場の全エリア平均）", x, y)

        x = ['リン吸(mg/100g)', 'P2O5(mg/100g)', ' ', '  ', '   ', '    ', '     ']
        y = [
            land_scores_agg['phosphorus_absorption__avg'],
            land_scores_agg['p2o5__avg'],
            0,
            0,
            0,
            0,
            0
        ]
        chart3 = g.plot_graph("リン酸関連（1圃場の全エリア平均）", x, y)

        x = ['CEC(meq/100g)', '腐植(%)', '仮比重', ' ', '  ', '   ', '    ']
        y = [
            land_scores_agg['cec__avg'],
            land_scores_agg['humus__avg'],
            land_scores_agg['bulk_density__avg'],
            0,
            0,
            0,
            0
        ]
        chart4 = g.plot_graph("土壌ポテンシャル関連（1圃場の全エリア平均）", x, y)

        context['chart1'] = chart1
        context['chart2'] = chart2
        context['chart3'] = chart3
        context['chart4'] = chart4
        context['company'] = Company(self.kwargs['company_id'])
        context['landledger'] = landledger
        context['landscores'] = landscores
        context['landreview'] = LandReview.objects.filter(landledger=landledger)

        return context


class UploadSoilhardnessView(FormView):
    template_name = 'crm/soilhardness/upload.html'
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
    template_name = 'crm/soilhardness/success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['import_errors'] = SoilHardnessMeasurementImportErrors.objects.all()
        return context
