import json
import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from locations.models import County, SubCounty, Constituency, Ward


class Command(BaseCommand):
    help = "Import counties, subcounties, constituencies, and wards from JSON file exported via phpMyAdmin"

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, help='URL to JSON file')
        parser.add_argument('--file', type=str, help='Local JSON file path')

    def handle(self, *args, **options):
        url = options.get('url')
        file_path = options.get('file')

        # --- Load JSON ---
        if url:
            self.stdout.write(self.style.WARNING(f"Fetching data from URL: {url}"))
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        elif file_path:
            self.stdout.write(self.style.WARNING(f"Loading data from file: {file_path}"))
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            self.stdout.write(self.style.ERROR("You must provide --url or --file"))
            return

        county_map = {}
        subcounty_map = {}
        const_map = {}

        with transaction.atomic():
            for table in data:
                if table.get("type") != "table":
                    continue

                name = table.get("name")
                rows = table.get("data", [])

                # --- Counties ---
                if name == "counties":
                    for rec in rows:
                        cid = rec.get("county_id")
                        cname = rec.get("county_name")
                        if not cid or not cname:
                            continue
                        county_obj, _ = County.objects.get_or_create(
                            name=cname.strip().title(),
                            defaults={"code": int(cid)},
                        )
                        county_map[cid] = county_obj

                # --- Subcounties ---
                elif name == "subcounties":
                    for rec in rows:
                        sid = rec.get("subcounty_id")
                        cid = rec.get("county_id")
                        sname = rec.get("constituency_name")
                        if not sid or not cid or not sname:
                            continue

                        county_obj = county_map.get(cid)
                        if not county_obj:
                            continue

                        sub_name = sname.strip().title()
                        sub_obj, _ = SubCounty.objects.get_or_create(
                            county=county_obj,
                            name=sub_name
                        )
                        subcounty_map[sid] = sub_obj

                        const_obj, _ = Constituency.objects.get_or_create(
                            name=sub_name,
                            sub_county=sub_obj
                        )
                        const_map[sub_name] = const_obj

                # --- Wards (stations) ---
                elif name == "station":
                    for rec in rows:
                        ward_name = rec.get("ward")
                        sid = rec.get("subcounty_id")
                        const_name = rec.get("constituency_name")

                        if not sid or not ward_name or not const_name:
                            continue

                        sub_obj = subcounty_map.get(sid)
                        if not sub_obj:
                            continue

                        c_name = const_name.strip().title()
                        const_obj = const_map.get(c_name)
                        if not const_obj:
                            const_obj, _ = Constituency.objects.get_or_create(
                                name=c_name,
                                sub_county=sub_obj
                            )
                            const_map[c_name] = const_obj

                        Ward.objects.get_or_create(
                            name=ward_name.strip().title(),
                            constituency=const_obj
                        )

        self.stdout.write(self.style.SUCCESS(" Import complete!"))
        self.stdout.write(self.style.SUCCESS(f"Counties: {County.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Subcounties: {SubCounty.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Constituencies: {Constituency.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Wards: {Ward.objects.count()}"))
