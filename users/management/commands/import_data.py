import pandas as pd
from django.core.management.base import BaseCommand
from users.models import Company


class Command(BaseCommand):
    help = 'Import company data from an Excel file'

    def handle(self, *args, **options):
        file_path = '/code/users/management/Data_To_Import/Company.xlsx'
        df = pd.read_excel(file_path)

        # Print column names for debugging
        self.stdout.write(f"Original Column names: {df.columns.tolist()}")

        # Check if the correct header is not in the first row and adjust
        if 'Name' not in df.columns:
            for i, row in df.iterrows():
                if 'Name' in row.values:
                    df.columns = row.values
                    df = df[i + 1:].reset_index(drop=True)
                    break

        self.stdout.write(f"Adjusted Column names: {df.columns.tolist()}")

        companies = []
        for index, row in df.iterrows():
            try:
                company_data = {
                    'name': row['Name'],
                    'symbol': row['Symbol'],
                    'name_on_website': row['Name on Website'],
                    'public_or_private': row['Public or Private'],
                    'industry': row['Industry'],
                    'industry_clean': row['Industry Clean'],
                    'sector': row['Sector'],
                    'clean_name': row['Clean Name'],
                    'website_url': row['Website URL']
                }
                companies.append(Company(**company_data))
            except KeyError as e:
                self.stdout.write(self.style.ERROR(f'Error importing row {index}: Missing column {e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Unexpected error importing row {index}: {e}'))

        # Bulk create all companies
        if companies:
            Company.objects.bulk_create(companies)
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(companies)} companies.'))
        else:
            self.stdout.write(self.style.WARNING('No companies were imported.'))