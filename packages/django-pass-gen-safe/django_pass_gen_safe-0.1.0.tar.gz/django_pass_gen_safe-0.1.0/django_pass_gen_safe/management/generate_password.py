from django.core.management.base import BaseCommand
import random
import string

class Command(BaseCommand):
    help = 'Génère un mot de passe sécurisé'

    def add_arguments(self, parser):
        parser.add_argument('--length', type=int, default=12, help='Longueur du mot de passe')
        parser.add_argument('--no-special', action='store_true', help='Exclure les caractères spéciaux')

    def handle(self, *args, **options):
        length = options['length']
        use_special = not options['no_special']

        letters = string.ascii_letters
        digits = string.digits
        special = string.punctuation
        all_chars = letters + digits + (special if use_special else '')

        password = ''.join(random.choice(all_chars) for _ in range(length))
        self.stdout.write(f"Mot de passe généré : {password}")