from django.shortcuts import render
def contact_list(request):
    return render(request, 'contacts/contacts.html')