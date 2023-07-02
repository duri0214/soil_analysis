import csv
import glob
import os
from datetime import datetime

import pytz

from django.core.management.base import BaseCommand

from crm.models import SoilHardnessMeasurement, SoilHardnessMeasurementImportErrors, Device


def extract_device(line: str) -> str:
    if line.strip()[:4] != 'DIK-':
        raise ValueError(f"Invalid device format: {line}")
    return line


def extract_setdatetime(line: str) -> datetime:
    try:
        temp = datetime.strptime(line.strip(), "%y.%m.%d %H:%M:%S")
        temp = pytz.timezone('Asia/Tokyo').localize(temp)
    except ValueError:
        raise ValueError(f"setdatetimeの値をdatetimeに変換できませんでした: {line}")
    return temp


def extract_numeric_value(line: str, value_name: str) -> int:
    try:
        temp = int(line.strip())
    except ValueError:
        raise ValueError(f"{value_name}の値をintに変換できませんでした: {line}")
    return temp


class Command(BaseCommand):
    help = 'Import soil hardness measurements from CSV'

    def add_arguments(self, parser):
        parser.add_argument('folder_path', type=str, help='Folder path containing CSV files')

    def handle(self, *args, **options):
        SoilHardnessMeasurementImportErrors.objects.all().delete()
        csv_files = glob.glob(os.path.join(options['folder_path'], '**/*.csv'), recursive=True)
        m_device = {device.name: device for device in Device.objects.all()}

        for csv_file in csv_files:
            parent_folder = os.path.basename(os.path.dirname(csv_file))

            try:
                with open(csv_file, newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)

                    # 1行目～10行目 から属性情報を取得
                    device = m_device[extract_device(next(reader)[0])]
                    memory = extract_numeric_value(next(reader)[1], 'memory')
                    next(reader)  # skip Latitude
                    next(reader)  # skip Longitude
                    setdepth = extract_numeric_value(next(reader)[1], 'setdepth')
                    setdatetime = extract_setdatetime(next(reader)[1])
                    setspring = extract_numeric_value(next(reader)[1], 'setspring')
                    setcone = extract_numeric_value(next(reader)[1], 'setcone')
                    next(reader)  # skip blank line
                    next(reader)  # skip header line

                    # 11行目以降のデータを保存
                    for row in reader:
                        SoilHardnessMeasurement.objects.create(
                            device=device,
                            memory=memory,
                            setdatetime=setdatetime,
                            setdepth=setdepth,
                            setspring=setspring,
                            setcone=setcone,
                            depth=int(row[0]),
                            pressure=int(row[1]),
                            csvfolder=parent_folder,
                        )
            except Exception as e:
                SoilHardnessMeasurementImportErrors.objects.create(
                    csvfile=os.path.basename(csv_file),
                    csvfolder=parent_folder,
                    message=str(e),
                )
                self.stderr.write(self.style.ERROR(
                    f'Error occurred while importing soil hardness measurements from {parent_folder}/{os.path.basename(csv_file)}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(
            'Successfully imported all soil hardness measurements from CSV files.'))
