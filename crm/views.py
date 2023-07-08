import os

from django.core.management import call_command
from django.db.models import Avg
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, TemplateView, FormView

from crm.domain.graph.graph_matplotlib import GraphMatplotlib
from crm.domain.valueobject.zipfileprocessor import ZipFileProcessor
from crm.forms import CompanyCreateForm, LandCreateForm, UploadZipForm
from crm.models import Company, Land, LandScoreChemical, LandReview, CompanyCategory, Ledger


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
        return super().get_queryset().filter(company=self.kwargs['company_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_id'] = self.kwargs['company_id']

        return context


class LandCreateView(CreateView):
    model = Land
    template_name = "crm/land/create.html"
    form_class = LandCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_id'] = self.kwargs['company_id']

        return context

    def form_valid(self, form):
        form.instance.company_id = self.kwargs['company_id']

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('crm:land_detail', kwargs={'company_id': self.kwargs['company_id'], 'pk': self.object.pk})


class LandDetailView(DetailView):
    model = Land
    template_name = 'crm/land/detail.html'


class LandReportChemicalListView(ListView):
    model = LandScoreChemical
    template_name = "crm/landreport/chemical.html"

    def get_queryset(self):
        return super().get_queryset().filter(land=self.kwargs['land_id'])

    def get_context_data(self, **kwargs):
        # LandScoreChemical
        land_score = LandScoreChemical.objects.filter(land=self.kwargs['land_id'])
        land_score_agg = land_score.aggregate(
            Avg('ec'), Avg('nh4n'), Avg('no3n'), Avg('total_nitrogen'), Avg('nh4_per_nitrogen'),
            Avg('ph'), Avg('cao'), Avg('mgo'), Avg('k2o'), Avg('base_saturation'), Avg('cao_per_mgo'),
            Avg('mgo_per_k2o'), Avg('phosphorus_absorption'), Avg('p2o5'), Avg('cec'), Avg('humus'),
            Avg('bulk_density'),
        )

        g = GraphMatplotlib()
        x = ['EC(mS/cm)', 'NH4-N(mg/100g)', 'NO3-N(mg/100g)', '無機態窒素', 'NH4/無機態窒素', ' ', '  ']
        y = [
            land_score_agg['ec__avg'],
            land_score_agg['nh4n__avg'],
            land_score_agg['no3n__avg'],
            land_score_agg['total_nitrogen__avg'],
            land_score_agg['nh4_per_nitrogen__avg'],
            0,
            0
        ]
        chart1 = g.plot_graph("窒素関連（1圃場の全エリア平均）", x, y)

        x = ['ph', 'CaO(mg/100g)', 'MgO(mg/100g)', 'K2O(mg/100g)', '塩基飽和度(%)', 'CaO/MgO', 'MgO/K2O']
        y = [
            land_score_agg['ph__avg'],
            land_score_agg['cao__avg'],
            land_score_agg['mgo__avg'],
            land_score_agg['k2o__avg'],
            land_score_agg['base_saturation__avg'],
            land_score_agg['cao_per_mgo__avg'],
            land_score_agg['mgo_per_k2o__avg']
        ]
        chart2 = g.plot_graph("塩基類関連（1圃場の全エリア平均）", x, y)

        x = ['リン吸(mg/100g)', 'P2O5(mg/100g)', ' ', '  ', '   ', '    ', '     ']
        y = [
            land_score_agg['phosphorus_absorption__avg'],
            land_score_agg['p2o5__avg'],
            0,
            0,
            0,
            0,
            0
        ]
        chart3 = g.plot_graph("リン酸関連（1圃場の全エリア平均）", x, y)

        x = ['CEC(meq/100g)', '腐植(%)', '仮比重', ' ', '  ', '   ', '    ']
        y = [
            land_score_agg['cec__avg'],
            land_score_agg['humus__avg'],
            land_score_agg['bulk_density__avg'],
            0,
            0,
            0,
            0
        ]
        chart4 = g.plot_graph("土壌ポテンシャル関連（1圃場の全エリア平均）", x, y)

        land_review = LandReview.objects.filter(land=self.kwargs['land_id'])
        context = super().get_context_data(**kwargs)
        context['chart_1'] = chart1
        context['chart_2'] = chart2
        context['chart_3'] = chart3
        context['chart_4'] = chart4
        context['company_id'] = self.kwargs['company_id']
        context['ledger'] = Ledger.objects.filter(land=self.kwargs['land_id'])
        context['land_review'] = land_review

        return context


class UploadSoilhardnessView(FormView):
    template_name = 'crm/soilhardness/upload.html'
    form_class = UploadZipForm
    success_url = reverse_lazy('crm:upload_soilhardness_success')

    def form_valid(self, form):
        # Zipを処理してバッチ実行
        upload_folder = ZipFileProcessor.handle_uploaded_zip(self.request.FILES['zipfile'])
        if os.path.exists(upload_folder):
            call_command('import_soil_hardness', upload_folder)

        return super().form_valid(form)


class UploadZipSuccessView(TemplateView):
    template_name = 'crm/soilhardness/success.html'
