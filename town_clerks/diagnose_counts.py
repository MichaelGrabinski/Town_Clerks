import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'town_clerks.settings')
django.setup()

from clerks.models import (
    Allmarriages, Marriagelicense, Civilunion, Marriagesfrombooks, # Marriage DB
    Vet, # Vets DB
    Transactions # Transmitel DB
)

print("\n--- Marriage DB Counts ---")
try:
    c = Allmarriages.objects.count()
    print(f"Allmarriages: {c}")
except Exception as e: print(f"Allmarriages error: {e}")

try:
    c = Marriagesfrombooks.objects.count()
    print(f"Marriagesfrombooks: {c}")
except Exception as e: print(f"Marriagesfrombooks error: {e}")

try:
    c = Marriagelicense.objects.count()
    print(f"Marriagelicense: {c}")
except Exception as e: print(f"Marriagelicense error: {e}")

try:
    c = Civilunion.objects.count()
    print(f"Civilunion: {c}")
except Exception as e: print(f"Civilunion error: {e}")


print("\n--- Vets DB Counts ---")
try:
    print(f"Vet: {Vet.objects.count()}")
except Exception as e: print(f"Vet error: {e}")

try:
    print(f"Refbranch: {Refbranch.objects.count()}")
except Exception as e: print(f"Refbranch error: {e}")


print("\n--- Transmitel DB Counts ---")
try:
    print(f"Transactions: {Transactions.objects.count()}")
except Exception as e: print(f"Transactions error: {e}")

try:
    print(f"Accounts: {Accounts.objects.count()}")
except Exception as e: print(f"Accounts error: {e}")
