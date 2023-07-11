from django.contrib.auth.models import User
from django.db import models


class CompanyCategory(models.Model):
    """
    顧客カテゴリマスタ
    name 名称 e.g. 農業法人
    """
    AGRI_COMPANY = 1

    name = models.CharField(max_length=256)
    remark = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.name


class Company(models.Model):
    """
    顧客マスタ
    name 名称 e.g. (有)アグリファクトリー
    """
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='company/', null=True, blank=True)
    remark = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    category = models.ForeignKey(CompanyCategory, on_delete=models.CASCADE)


class Crop(models.Model):
    """
    作物マスタ
    name    作物名 e.g. キャベツ、レタスなど
    """
    name = models.CharField(max_length=256)
    remark = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)


class LandBlock(models.Model):
    """
    圃場ブロックマスタ
    name        エリア名    e.g. A1
    """
    name = models.CharField(max_length=256)
    remark = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="name_unique"
            ),
        ]


class LandPeriod(models.Model):
    """
    時期マスタ
    year    西暦年      e.g. 2022
    name    時期の名前   e.g. 定植時
    """
    year = models.IntegerField()
    name = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["year", "name"],
                name="year_name_unique"
            ),
        ]


class CultivationType(models.Model):
    """
    作型マスタ
    name    作型の名前   e.g. 路地、ビニールハウス
    """
    name = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.name


class Land(models.Model):
    """
    圃場マスタ
    name        圃場名
    prefecture  都道府県    e.g. 茨城県
    location    住所       e.g. 結城郡八千代町
    latlon      緯度経度    e.g. 36.164677272061,139.86772928159
    area        面積       e.g. 100㎡
    image       写真
    remark      備考
    company     法人[FK]
    owner       オーナー    e.g. Ａ生産者
    cultivation_type 作型  e.g. 露地、ビニールハウス
    """
    name = models.CharField(max_length=256)
    prefecture = models.CharField(max_length=256)
    location = models.CharField(max_length=256)
    latlon = models.CharField(null=True, blank=True, max_length=256)
    area = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to='land/', null=True, blank=True)
    remark = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    cultivation_type = models.ForeignKey(CultivationType, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class SamplingMethod(models.Model):
    """
    採土法マスタ e.g. 5点法
    """
    name = models.CharField(max_length=256)
    remark = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)


class LandLedger(models.Model):
    """
    採土した日についてまとめる台帳
    採土日, 採土法, 採土者, 分析依頼日, 報告日, 分析機関, 分析番号
    """
    sampling_date = models.DateField()
    analysis_request_date = models.DateField(null=True)
    reporting_date = models.DateField(null=True)
    analysis_number = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    analytical_agency = models.ForeignKey(Company, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    land = models.ForeignKey(Land, on_delete=models.CASCADE)
    landperiod = models.ForeignKey(LandPeriod, on_delete=models.CASCADE)
    sampling_method = models.ForeignKey(SamplingMethod, on_delete=models.CASCADE)
    sampling_staff = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["land", "landperiod"],
                name="land_landperiod_unique"
            ),
        ]


class LandScoreChemical(models.Model):
    """
    顧客が持つ圃場をエリア単位で１レコードに収録します
    圃場ひとつは９つのエリアに分かれるが計測は5エリア✕5箇所で、1圃場あたり25箇所計測
    ec                      電気伝導率 e.g. 1(mS/cm)
    nh4n                    アンモニア態窒素 e.g. 1(mg/100g)
    no3n                    硝酸態窒素 e.g. 1(mg/100g)
    total_nitrogen          無機態窒素（NH4＋NO3）
    nh4_per_nitrogen        アンモニア態窒素比
    ph                      水素イオン濃度
    cao                     交換性石灰
    mgo                     交換性苦土
    k2o                     交換性加里
    base_saturation         塩基飽和度 e.g. 0.57
    cao_per_mgo             CaO/MgO e.g. 0.57
    mgo_per_k2o             MgO/K2O e.g. 0.57
    phosphorus_absorption   リン酸吸収係数
    p2o5                    可給態リン酸
    cec                     塩基置換容量
    humus                   腐植
    bulk_density            仮比重
    """
    ec = models.FloatField(null=True)
    nh4n = models.FloatField(null=True)
    no3n = models.FloatField(null=True)
    total_nitrogen = models.FloatField(null=True)
    nh4_per_nitrogen = models.FloatField(null=True)
    ph = models.FloatField(null=True)
    cao = models.FloatField(null=True)
    mgo = models.FloatField(null=True)
    k2o = models.FloatField(null=True)
    base_saturation = models.FloatField(null=True)
    cao_per_mgo = models.FloatField(null=True)
    mgo_per_k2o = models.FloatField(null=True)
    phosphorus_absorption = models.FloatField(null=True)
    p2o5 = models.FloatField(null=True)
    cec = models.FloatField(null=True)
    humus = models.FloatField(null=True)
    bulk_density = models.FloatField(null=True)
    remark = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    landblock = models.ForeignKey(LandBlock, on_delete=models.CASCADE)
    landledger = models.ForeignKey(LandLedger, on_delete=models.CASCADE)


class LandReview(models.Model):
    """
    顧客が持つ圃場にperiod単位で評価コメントをつける
    remarkはあくまで定型的につけたもの（commentが主体）
    """
    comment = models.TextField()
    remark = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    landledger = models.ForeignKey(LandLedger, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["landledger"],
                name="landledger_unique"
            ),
        ]


class Device(models.Model):
    """
    土壌硬度計マスタ
    """
    name = models.CharField(max_length=256)
    remark = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)


class SoilHardnessMeasurement(models.Model):
    """
    土壌硬度測定 生データ
    """
    setmemory = models.IntegerField()
    setdatetime = models.DateTimeField()
    setdepth = models.IntegerField()
    setspring = models.IntegerField()
    setcone = models.IntegerField()
    depth = models.IntegerField()
    pressure = models.IntegerField()
    csvfolder = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    setdevice = models.ForeignKey(Device, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["setdevice", "setmemory", "setdatetime", "depth"],
                name="setdevice_setmemory_setdatetime_depth_unique"
            ),
        ]


class SoilHardnessMeasurementImportErrors(models.Model):
    """
    土壌硬度測定 生データ 取り込みエラーリスト
    """
    csvfile = models.CharField(max_length=256)
    csvfolder = models.CharField(max_length=256)
    message = models.TextField()
    remark = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
