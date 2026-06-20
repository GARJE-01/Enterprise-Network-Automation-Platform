import os
import difflib
from datetime import datetime

BACKUP_DIR = "../backups"
REPORT_DIR = "../drift_reports"

os.makedirs(REPORT_DIR, exist_ok=True)

# Get backup folders sorted by date
backup_sets = sorted(
    [f for f in os.listdir(BACKUP_DIR)
     if os.path.isdir(os.path.join(BACKUP_DIR, f))]
)

if len(backup_sets) < 2:
    print("Need at least 2 backup sets.")
    exit()

old_backup = backup_sets[-2]
new_backup = backup_sets[-1]

print(f"Comparing:")
print(f"OLD: {old_backup}")
print(f"NEW: {new_backup}")

old_path = os.path.join(BACKUP_DIR, old_backup)
new_path = os.path.join(BACKUP_DIR, new_backup)

report_file = os.path.join(
    REPORT_DIR,
    f"drift_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
)

with open(report_file, "w", encoding="utf-8") as report:

    report.write("=" * 60 + "\n")
    report.write("CONFIGURATION DRIFT REPORT\n")
    report.write("=" * 60 + "\n\n")

    for device_file in os.listdir(new_path):

        old_file = os.path.join(old_path, device_file)
        new_file = os.path.join(new_path, device_file)

        if not os.path.exists(old_file):
            continue

        with open(old_file, "r", encoding="utf-8") as f:
            old_config = f.readlines()

        with open(new_file, "r", encoding="utf-8") as f:
            new_config = f.readlines()

        diff = list(
            difflib.unified_diff(
                old_config,
                new_config,
                fromfile=old_backup,
                tofile=new_backup,
                lineterm=""
            )
        )

        report.write(f"\n{'='*60}\n")
        report.write(f"DEVICE: {device_file}\n")
        report.write(f"{'='*60}\n")

        if diff:
            report.write("\n".join(diff))
        else:
            report.write("NO CHANGES DETECTED")

        report.write("\n\n")

print(f"\nDrift report created:")
print(report_file)