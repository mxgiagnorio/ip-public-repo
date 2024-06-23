# capa de vista/presentación
# si se necesita algún dato (lista, valor, etc), esta capa SIEMPRE se comunica con services_nasa_image_gallery.py

from django.shortcuts import redirect, render
from .layers.services import services_nasa_image_gallery
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.paginator import Paginator
from googletrans import Translator
from langdetect import detect
from django.contrib import messages


# función que invoca al template del índice de la aplicación.
def index_page(request):
    return render(request, 'index.html')

# auxiliar: retorna 2 listados -> uno de las imágenes de la API y otro de los favoritos del usuario.
def getAllImagesAndFavouriteList(request):
    images = services_nasa_image_gallery.getAllImages()
    favourite_list = []

    return images, favourite_list

# función principal de la galería.
def home(request):
    # llama a la función auxiliar getAllImagesAndFavouriteList() y obtiene 2 listados: uno de las imágenes de la API y otro de favoritos por usuario*.
    # (*) este último, solo si se desarrolló el opcional de favoritos; caso contrario, será un listado vacío [].
    images = services_nasa_image_gallery.getAllImages()
    favourite_list = []

# Paginación
    page_number = request.GET.get("page", 1)
    items_per_page = request.GET.get("itemsPerPage", 5)

    paginator = Paginator(images, items_per_page)
    page_obj = paginator.get_page(page_number)

    return render(request, 'home.html', {'page_obj': page_obj, 'favourite_list': favourite_list, 'items_per_page': items_per_page})


# función utilizada en el buscador.
def search(request):
    search_msg = request.GET.get('query', '')
    favourite_list = []

    if search_msg == "":
        return redirect(home)
    else:
        # Detectar el idioma de la consulta
        detected_language = detect(search_msg)
        
        # Traducir la consulta de búsqueda solo si no está en inglés
        if detected_language != 'en':
            translator = Translator()
            translated_query = translator.translate(search_msg, src='es', dest='en').text
        else:
            translated_query = search_msg

        search_images = services_nasa_image_gallery.getAllImages(translated_query)

        # Paginación
        page_number = request.GET.get("page", 1)
        items_per_page = request.GET.get("itemsPerPage", 5)

        paginator = Paginator(search_images, items_per_page)
        page_obj = paginator.get_page(page_number)

        return render(
            request,
            "home.html",
            {"query": search_msg, "page_obj": page_obj, "favourite_list": favourite_list, "items_per_page": items_per_page}
        )
    


    # si el usuario no ingresó texto alguno, debe refrescar la página; caso contrario, debe filtrar aquellas imágenes que posean el texto de búsqueda.


# las siguientes funciones se utilizan para implementar la sección de favoritos: traer los favoritos de un usuario, guardarlos, eliminarlos y desloguearse de la app.
@login_required
def getAllFavouritesByUser(request):
    favourite_list = services_nasa_image_gallery.getAllFavouritesByUser(request)
    return render(request, 'favourites.html', {'favourite_list': favourite_list})


@login_required
def saveFavourite(request):
    if request.method == 'POST':
        comentario = request.POST.get('comentario')
        fav = services_nasa_image_gallery.saveFavourite(request,comentario)
        if fav:
            messages.success(request, '¡La imagen se ha guardado en favoritos correctamente!')
            return redirect('home')
        else:
            messages.info(request, '¡La imagen ya está guardada en favoritos!')
            return redirect('home')

@login_required
def deleteFavourite(request):
    if request.method == 'POST':
        success = services_nasa_image_gallery.deleteFavourite(request)
        if success:
            return redirect('favoritos')
        else:
            return redirect('favoritos')


@login_required
def exit(request):
    logout(request)
    return redirect('index-page')