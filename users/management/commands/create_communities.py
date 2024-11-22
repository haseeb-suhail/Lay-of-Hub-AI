from django.core.management.base import BaseCommand
from users.models import Community

class Command(BaseCommand):
    help = 'Create initial communities'

    def handle(self, *args, **options):
        communities = [
            "Technology Enthusiasts", "Software Developers", "Hardware Geeks", "Mobile Technology", "Web Development",
            "AI & Machine Learning", "Cybersecurity", "Data Science", "Cloud Computing", "Blockchain Enthusiasts",
            "IoT Innovators", "Game Development", "Networking Experts", "Tech News", "Startups & Entrepreneurs",
            "Open Source Projects", "Tech Events", "Career Advice in Tech", "Tech Education", "Tech Support",
            "Freelancers", "UI/UX Design", "DevOps", "Programming Languages", "IT Professionals",
            "Robotics", "Virtual Reality", "Augmented Reality", "Tech Podcasts", "Coding Challenges",
            "Tech Books", "Women in Tech", "Ethical Hacking", "IT Certifications", "Tech Reviews",
            "Server Administration", "Software Testing", "Mobile Apps Development", "Tech Innovations",
            "E-commerce Development", "Tech Gadgets", "Artificial Intelligence", "Machine Learning", "Big Data",
            "Tech Jobs", "Tech Trends", "Project Management", "Tech Tutorials", "Software Architecture",
            "Tech Startups", "Tech Investment", "Digital Marketing", "SEO & SEM", "Content Management",
            "Cloud Services", "SaaS", "PaaS", "IaaS", "Cyber Threats", "IT Governance", "Data Privacy",
            "IT Law & Compliance", "Tech Partnerships", "Innovation Labs", "IT Infrastructure",
            "Agile Methodologies", "Scrum Masters", "Product Management", "Technical Writing", "Quality Assurance",
            "IT Outsourcing", "Tech Networking", "IT Strategy", "Business Intelligence", "Data Warehousing",
            "IT Consulting", "Mobile Gaming", "Tech Health", "IT Ethics", "Green Technology", "Tech Incubators",
            "Tech Crowdfunding", "Digital Transformation", "Smart Cities", "Wearable Technology", "Tech Culture",
            "Remote Work", "Tech Ecosystems", "IT Service Management", "Disaster Recovery", "Tech Policy",
            "IT Procurement", "Enterprise Architecture", "Tech Conferences", "Tech Communities", "IT Leadership",
            "Tech Mentorship", "Tech Volunteers", "Open Innovation", "Smart Homes"
        ]

        for name in communities:
            Community.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS('Successfully created communities'))
