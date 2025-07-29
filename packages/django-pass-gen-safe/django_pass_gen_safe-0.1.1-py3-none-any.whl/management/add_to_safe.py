from django.core.management.base import BaseCommand
from django_pass_gen_safe.utils import load_safe, save_safe

class Command(BaseCommand):
    help = 'Ajoute un mot de passe au trousseau'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Nom d\'identification du mot de passe')
        parser.add_argument('password', type=str, help='Mot de passe à sauvegarder')

    def handle(self, *args, **options):
        name = options['name']
        password = options['password']
        safe = load_safe()
        if name in safe:
            self.stdout.write(f"Le nom '{name}' existe déjà !")
        else:
            safe[name] = password  # À chiffrer dans une version sécurisée
            save_safe(safe)
            self.stdout.write(f"Mot de passe '{name}' ajouté au trousseau !")