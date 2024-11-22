import pandas as pd
from django.core.management.base import BaseCommand
from users.models import Sector

class Command(BaseCommand):
    help = 'Import sector data from an Excel file'

    def handle(self, *args, **options):
        file_path = '/code/users/management/Data_To_Import/Sector.xlsx'
        df = pd.read_excel(file_path)

        # Print column names for debugging
        self.stdout.write(f"Original Column names: {df.columns.tolist()}")

        # Check if the correct header is not in the first row and adjust
        if 'Sub Sector' not in df.columns:
            for i, row in df.iterrows():
                if 'Sub Sector' in row.values:
                    df.columns = row.values
                    df = df[i + 1:].reset_index(drop=True)
                    break

        self.stdout.write(f"Adjusted Column names: {df.columns.tolist()}")

        sectors = []
        for index, row in df.iterrows():
            try:
                sector_data = {
                    'sub_sector': row['Sub Sector'],
                    'industry': row['Industry'],
                    'sector': row['Sector'],
                }
                sectors.append(Sector(**sector_data))
            except KeyError as e:
                self.stdout.write(self.style.ERROR(f'Error importing row {index}: Missing column {e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Unexpected error importing row {index}: {e}'))

        # Bulk create all sectors
        if sectors:
            Sector.objects.bulk_create(sectors)
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(sectors)} sectors.'))
        else:
            self.stdout.write(self.style.WARNING('No sectors were imported.'))
