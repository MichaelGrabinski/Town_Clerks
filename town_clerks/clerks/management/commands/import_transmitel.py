from django.core.management.base import BaseCommand
import pandas as pd
import json
from clerks.models import TransmitelReport

class Command(BaseCommand):
    help = 'Import a transmitel CSV/XLSX and store headers/data'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Path to CSV or Excel file')

    def handle(self, *args, **options):
        p = options['path']
        if p.endswith('.xlsx') or p.endswith('.xls'):
            df = pd.read_excel(p)
        else:
            df = pd.read_csv(p)
        headers = list(df.columns)
        self.stdout.write(f'Found headers: {headers}')
        report = TransmitelReport.objects.create(filename=p, data=json.loads(df.to_json(orient='records')))
        self.stdout.write(f'Imported report id={report.id}')
