import json
from django.core.management.base import BaseCommand
from schemes.models import Scheme


class Command(BaseCommand):
    help = 'Populate database with sample government schemes'

    def handle(self, *args, **options):
        sample_schemes = [
            {
                'scheme_name': 'PM Kisan Samman Nidhi',
                'details': 'Under this scheme, income support of Rs. 6,000/- per year is provided to small and marginal farmer families having combined land holding/ownership of up to 2 hectares.',
                'benefits': 'Financial assistance of Rs. 6,000 per year in three equal installments of Rs. 2,000 each.',
                'eligibility': 'Small and marginal farmers with landholding up to 2 hectares. Must be an Indian citizen.',
                'application': 'Apply online through PM Kisan portal or visit nearest Common Service Centre.',
                'documents': 'Aadhaar Card, Bank Account Details, Land Ownership Certificate, Ration Card',
                'level': 'central',
                'scheme_category': 'agriculture',
                'ministry_department': 'Ministry of Agriculture and Farmers Welfare',
                'website_url': 'https://pmkisan.gov.in'
            },
            {
                'scheme_name': 'Pradhan Mantri Awas Yojana',
                'details': 'Housing scheme to provide affordable housing to urban and rural poor with a target of constructing 2 crore houses.',
                'benefits': 'Subsidy on home loans, direct assistance for house construction',
                'eligibility': 'Families not owning a pucca house, annual income criteria varies by category',
                'application': 'Apply through PMAY portal or nearest bank',
                'documents': 'Aadhaar Card, Income Certificate, Non-ownership Certificate, Bank Details',
                'level': 'central',
                'scheme_category': 'housing',
                'ministry_department': 'Ministry of Housing and Urban Affairs',
                'website_url': 'https://pmaymis.gov.in'
            },
            {
                'scheme_name': 'Ayushman Bharat - PM JAY',
                'details': 'World largest health insurance scheme providing coverage of Rs. 5 lakhs per family per year for secondary and tertiary care hospitalization.',
                'benefits': 'Health insurance coverage up to Rs. 5 lakhs per family per year',
                'eligibility': 'Families listed in SECC-2011 database, rural and urban poor families',
                'application': 'No application required, eligible families automatically covered',
                'documents': 'Ration Card, Aadhaar Card for identification at hospitals',
                'level': 'central',
                'scheme_category': 'healthcare',
                'ministry_department': 'Ministry of Health and Family Welfare',
                'website_url': 'https://pmjay.gov.in'
            },
            {
                'scheme_name': 'Beti Bachao Beti Padhao',
                'details': 'Scheme to address declining Child Sex Ratio and related issues of empowerment of women over a life-cycle continuum.',
                'benefits': 'Awareness campaigns, educational support, skill development for girls',
                'eligibility': 'All girl children, especially in districts with low CSR',
                'application': 'Implemented through various government schemes and programs',
                'documents': 'Birth Certificate, School Records, Aadhaar Card',
                'level': 'central',
                'scheme_category': 'women_child',
                'ministry_department': 'Ministry of Women and Child Development',
                'website_url': 'https://wcd.nic.in'
            },
            {
                'scheme_name': 'Pradhan Mantri Mudra Yojana',
                'details': 'Provides loans up to 10 lakh to non-corporate, non-farm small/micro enterprises.',
                'benefits': 'Collateral-free loans up to Rs. 10 lakhs for business activities',
                'eligibility': 'Non-corporate, non-farm income generating activities, existing business owners',
                'application': 'Apply through participating banks and financial institutions',
                'documents': 'Business Plan, Identity Proof, Address Proof, Income Proof',
                'level': 'central',
                'scheme_category': 'financial_inclusion',
                'ministry_department': 'Ministry of Finance',
                'website_url': 'https://mudra.org.in'
            },
            {
                'scheme_name': 'Mahatma Gandhi NREGA',
                'details': 'Provides at least 100 days of guaranteed wage employment to every household whose adult members volunteer to do unskilled manual work.',
                'benefits': '100 days guaranteed employment, minimum wage payment',
                'eligibility': 'Adult members of rural households willing to do manual work',
                'application': 'Apply for job card at Gram Panchayat',
                'documents': 'Aadhaar Card, Address Proof, Bank Account Details',
                'level': 'central',
                'scheme_category': 'employment',
                'ministry_department': 'Ministry of Rural Development',
                'website_url': 'https://nrega.nic.in'
            },
            {
                'scheme_name': 'Pradhan Mantri Scholarship Scheme',
                'details': 'Scholarship for wards of Ex-servicemen and Ex-Coast Guard personnel for professional and technical courses.',
                'benefits': 'Financial assistance for education, monthly scholarship amount',
                'eligibility': 'Children of ex-servicemen, good academic record, age below 27 years',
                'application': 'Apply online through National Scholarship Portal',
                'documents': 'Educational Certificates, Ex-servicemen Certificate, Income Certificate',
                'level': 'central',
                'scheme_category': 'education',
                'ministry_department': 'Ministry of Defence',
                'website_url': 'https://scholarships.gov.in'
            },
            {
                'scheme_name': 'Pradhan Mantri Kaushal Vikas Yojana',
                'details': 'Skill development scheme to enable Indian youth to take up industry-relevant skill training.',
                'benefits': 'Free skill training, certification, placement assistance, monetary rewards',
                'eligibility': 'Indian youth aged 18-35 years who are school/college dropouts or unemployed',
                'application': 'Enroll through training centers or online portal',
                'documents': 'Aadhaar Card, Educational Certificates, Bank Account Details',
                'level': 'central',
                'scheme_category': 'skill_development',
                'ministry_department': 'Ministry of Skill Development and Entrepreneurship',
                'website_url': 'https://pmkvyofficial.org'
            }
        ]

        created_count = 0
        for scheme_data in sample_schemes:
            scheme, created = Scheme.objects.get_or_create(
                scheme_name=scheme_data['scheme_name'],
                defaults=scheme_data
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created: {scheme.scheme_name}")
            else:
                self.stdout.write(f"Already exists: {scheme.scheme_name}")

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new schemes')
        )
