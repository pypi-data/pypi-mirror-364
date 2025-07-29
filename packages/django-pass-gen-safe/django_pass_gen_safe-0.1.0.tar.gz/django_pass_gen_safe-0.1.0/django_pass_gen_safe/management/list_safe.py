from django.core.management.base import BaseCommand
from django_pass_gen_safe.utils import load_safe

class Command(BaseCommand):
    help = 'Liste les noms des mots de passe stockés'

    def handle(self, *args, **options):
        safe = load_safe()
        if safe:
            self.stdout.write("Mots de passe stockés :")
            for name in safe.keys():
                self.stdout.write(f"- {name}")
        else:
            self.stdout.write("Aucun mot de passe stocké.")