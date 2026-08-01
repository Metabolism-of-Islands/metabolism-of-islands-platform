from django.shortcuts import render
from django.contrib import messages
from main.models import *

def index(request):

    # TEMP MIGRATION CODE

    if "migrate" in request.GET:
        migrate = request.GET["migrate"]
        if migrate == "1":
            ReferenceSpace.objects.filter(activated__isnull=True).delete()
            messages.success(request, "Non-activated reference spaces are deleted; only islands remain")
        elif migrate == "2":
            regions = [
                ("AIMS Region", "Other"),
                ("American Samoa", "Pacific Ocean"),
                ("Antigua & Barbuda", "Caribbean"),
                ("Aruba", "Caribbean"),
                ("Bahamas", "Caribbean"),
                ("Barbados", "Caribbean"),
                ("Belize", "Caribbean"),
                ("British Virgin Islands", "Caribbean"),
                ("Cabo Verde", "Other"),
                ("Canary Islands", "Other"),
                ("Caribbean Region", "Other"),
                ("Comoros", "Indian Ocean"),
                ("Cook Islands", "Pacific Ocean"),
                ("Crete", "Other"),
                ("Cuba", "Caribbean"),
                ("Curacao", "Caribbean"),
                ("Cyprus", "Other"),
                ("Dominica", "Caribbean"),
                ("Dominican Republic", "Caribbean"),
                ("Faroe Islands", "Other"),
                ("Fiji", "Pacific Ocean"),
                ("Galapagos Islands", "Pacific Ocean"),
                ("Grenada", "Caribbean"),
                ("Guadeloupe", "Caribbean"),
                ("Guam", "Pacific Ocean"),
                ("Guinea-Bissau", "Other"),
                ("Guyana", "Other"),
                ("Haiti", "Caribbean"),
                ("Hawaii", "Pacific Ocean"),
                ("Hong Kong", "Other"),
                ("Jamaica", "Caribbean"),
                ("Kiribati", "Pacific Ocean"),
                ("Madagascar", "Indian Ocean"),
                ("Maldives", "Indian Ocean"),
                ("Mallorca", "Other"),
                ("malta", "Other"),
                ("Marshall Islands", "Pacific Ocean"),
                ("Martinique", "Caribbean"),
                ("Mauritius", "Indian Ocean"),
                ("Micronesia", "Pacific Ocean"),
                ("Nauru", "Pacific Ocean"),
                ("New Caledonia", "Pacific Ocean"),
                ("Niue", "Pacific Ocean"),
                ("Northern Mariana Islands (CNMI)", "Pacific Ocean"),
                ("Oahu", "Pacific Ocean"),
                ("Okinawa", "Pacific Ocean"),
                ("Pacific Region", "Other"),
                ("Palau", "Pacific Ocean"),
                ("Papua New Guinea", "Pacific Ocean"),
                ("Réunion Island", "Indian Ocean"),
                ("Saint Kitts and Nevis", "Caribbean"),
                ("Saint Lucia", "Caribbean"),
                ("Saint Vincent and the Grenadines", "Caribbean"),
                ("Samoa", "Pacific Ocean"),
                ("Samothraki Island", "Other"),
                ("Sardinia", "Other"),
                ("Seychelles", "Indian Ocean"),
                ("Singapore", "Indian Ocean"),
                ("Sint Maarten", "Caribbean"),
                ("Solomon Islands", "Pacific Ocean"),
                ("Timor-Leste", "Other"),
                ("Tonga", "Pacific Ocean"),
                ("Trinidad and Tobago", "Caribbean"),
                ("Trinket Island", "Other"),
                ("Tuvalu", "Pacific Ocean"),
                ("Vanuatu", "Pacific Ocean"),
            ]
            regions = dict(regions)
            islands = Island.objects.all()
            for each in islands:
                e = str(each)
                e = e.strip()
                print(each, regions[e])
                

    # END OF MIGRATION CODE

    islands = Island.objects.all()
    context = {
        "islands": islands,
    }
    return render(request, "main/index.html", context)
